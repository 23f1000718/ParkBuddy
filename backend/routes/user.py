from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from ..models import ParkingLot, ParkingSpot, Reservation, User
from ..extensions import db, cache
from .decorators import role_required
from datetime import datetime

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
    res.parking_cost = round(duration_hours * rate, 2)

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
@cache.cached(timeout=300)  # Cache for 5 minutes
def user_stats():
    user_id = int(get_jwt_identity())
    
    # Get user statistics
    total_reservations = Reservation.query.filter_by(user_id=user_id).count()
    completed_reservations = Reservation.query.filter_by(
        user_id=user_id
    ).filter(Reservation.leaving_timestamp.isnot(None)).count()
    
    total_cost = db.session.query(db.func.sum(Reservation.parking_cost)).filter_by(
        user_id=user_id
    ).scalar() or 0
    
    # Most used parking lot with explicit joins
    lot_usage = db.session.query(
        ParkingLot.prime_location_name,
        db.func.count(Reservation.id)
    ).select_from(Reservation).join(
        ParkingSpot, Reservation.spot_id == ParkingSpot.id
    ).join(
        ParkingLot, ParkingSpot.lot_id == ParkingLot.id
    ).filter(
        Reservation.user_id == user_id
    ).group_by(
        ParkingLot.prime_location_name
    ).order_by(
        db.func.count(Reservation.id).desc()
    ).first()
    
    return jsonify({
        "total_reservations": total_reservations,
        "completed_reservations": completed_reservations,
        "total_cost": float(total_cost),
        "most_used_lot": lot_usage[0] if lot_usage else "None"
    })
