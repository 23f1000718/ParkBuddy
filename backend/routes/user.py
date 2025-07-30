from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from ..models import ParkingLot, ParkingSpot, Reservation, User
from ..extensions import db, cache
from .decorators import role_required
from datetime import datetime, timedelta
from sqlalchemy import func

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/user/lots', methods=['GET'])
@role_required('user')
def get_lots():
    lots = ParkingLot.query.all()
    return jsonify([
        {
            "id": lot.id,
            "prime_location_name": lot.prime_location_name,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "price_per_hour": lot.price_per_hour,
            "available_spots": len([s for s in lot.spots if s.status == 'A'])
        }
        for lot in lots
    ])

@user_bp.route('/api/user/reserve/<int:lot_id>', methods=['POST'])
@role_required('user')
def reserve_api(lot_id):
    user_id = int(get_jwt_identity())
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not spot:
        return jsonify(msg="No available spots"), 404

    spot.status = 'O'
    reservation = Reservation(user_id=user_id, spot_id=spot.id)
    db.session.add(reservation)
    db.session.commit()
    return jsonify(msg="Reserved", reservation_id=reservation.id), 200

@user_bp.route('/api/user/release/<int:res_id>', methods=['POST'])
@role_required('user')
def release(res_id):
    res = Reservation.query.get_or_404(res_id)
    if res.leaving_timestamp:
        return jsonify(msg="Already released"), 400

    res.leaving_timestamp = datetime.utcnow()
    res.spot.status = 'A'

    duration_hours = (res.leaving_timestamp - res.parking_timestamp).total_seconds() / 3600
    rate = res.spot.lot.price_per_hour
    
    # Minimum billing: 1 hour, then charge for actual time if more than 1 hour
    billable_hours = max(1.0, duration_hours)
    res.parking_cost = round(billable_hours * rate, 2)

    db.session.commit()
    return jsonify(msg="Spot released", cost=res.parking_cost), 200

@user_bp.route('/api/user/reservations', methods=['GET'])
@role_required('user')
def history():
    user_id = int(get_jwt_identity())
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            "id": res.id,
            "spot_id": res.spot_id,
            "lot": res.spot.lot.prime_location_name,
            "start": res.parking_timestamp.strftime("%Y-%m-%d %H:%M"),
            "end": res.leaving_timestamp.strftime("%Y-%m-%d %H:%M") if res.leaving_timestamp else None,
            "cost": res.parking_cost,
            "status": "Active" if not res.leaving_timestamp else "Completed"
        }
        for res in reservations
    ])

@user_bp.route('/api/user/active-reservations', methods=['GET'])
@role_required('user')
def active_reservations():
    user_id = int(get_jwt_identity())
    active_reservations = Reservation.query.filter_by(
        user_id=user_id, 
        leaving_timestamp=None
    ).all()
    
    return jsonify([
        {
            "id": res.id,
            "spot_id": res.spot_id,
            "lot": res.spot.lot.prime_location_name,
            "start": res.parking_timestamp.strftime("%Y-%m-%d %H:%M"),
            "parking_duration": round((datetime.utcnow() - res.parking_timestamp).total_seconds() / 3600, 2)
        }
        for res in active_reservations
    ])

@user_bp.route('/api/user/export-csv', methods=['POST'])
@role_required('user')
def trigger_csv_export():
    user_id = int(get_jwt_identity())
    # Import tasks here to avoid circular import
    from ..tasks import export_user_csv
    # Trigger background job
    task = export_user_csv.delay(user_id)
    return jsonify(msg="CSV export started", task_id=task.id), 200

@user_bp.route('/api/user/stats', methods=['GET'])
@role_required('user')
def user_stats():
    user_id = int(get_jwt_identity())
    try:
        # General Stats
        total_reservations = Reservation.query.filter_by(user_id=user_id).count()
        completed_reservations = Reservation.query.filter_by(user_id=user_id).filter(Reservation.leaving_timestamp.isnot(None)).count()
        active_reservations = total_reservations - completed_reservations
        total_cost = db.session.query(func.sum(Reservation.parking_cost)).filter_by(user_id=user_id).scalar() or 0

        # Monthly spending data for the last 6 months
        from datetime import datetime, timedelta
        from sqlalchemy import extract
        
        monthly_spending = []
        current_date = datetime.now()
        
        for i in range(6):
            # Calculate the month and year for each of the last 6 months
            month_date = current_date - timedelta(days=30 * i)
            month_cost = db.session.query(func.sum(Reservation.parking_cost)).filter(
                Reservation.user_id == user_id,
                extract('month', Reservation.leaving_timestamp) == month_date.month,
                extract('year', Reservation.leaving_timestamp) == month_date.year,
                Reservation.leaving_timestamp.isnot(None)
            ).scalar() or 0
            
            monthly_spending.insert(0, {
                "month": month_date.strftime("%b %Y"),
                "amount": float(month_cost)
            })

        # Most used parking lots
        lot_usage = db.session.query(
            ParkingLot.prime_location_name,
            func.count(Reservation.id).label('usage_count')
        ).join(ParkingSpot, ParkingLot.id == ParkingSpot.lot_id)\
         .join(Reservation, ParkingSpot.id == Reservation.spot_id)\
         .filter(Reservation.user_id == user_id)\
         .group_by(ParkingLot.id)\
         .order_by(func.count(Reservation.id).desc())\
         .limit(5).all()

        lot_usage_data = [
            {"name": lot[0], "count": lot[1]} 
            for lot in lot_usage
        ]

        return jsonify({
            "total_reservations": total_reservations,
            "completed_reservations": completed_reservations,
            "active_reservations": active_reservations,
            "total_cost": float(total_cost),
            "monthly_spending": monthly_spending,
            "lot_usage": lot_usage_data
        })
    except Exception as e:
        import traceback
        print("Error in user_stats:", e)
        print(traceback.format_exc())
        return jsonify(msg="Error loading statistics", error=str(e)), 500
