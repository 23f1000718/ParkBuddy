from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, ParkingLot, ParkingSpot, Reservation, Admin
from ..extensions import db, cache
from .decorators import role_required
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/lots', methods=['GET'])
@role_required('admin')
def get_all_lots():
    lots = ParkingLot.query.all()
    return jsonify([
        {
            "id": lot.id,
            "prime_location_name": lot.prime_location_name,
            "price_per_hour": lot.price_per_hour,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "number_of_spots": lot.number_of_spots
        }
        for lot in lots
    ])

@admin_bp.route('/api/lots/<int:lot_id>', methods=['GET'])
@role_required('admin')
def get_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    return jsonify({
        "id": lot.id,
        "prime_location_name": lot.prime_location_name,
        "price_per_hour": lot.price_per_hour,
        "address": lot.address,
        "pin_code": lot.pin_code,
        "number_of_spots": lot.number_of_spots
    })

@admin_bp.route('/api/lots/<int:lot_id>', methods=['DELETE'])
@role_required('admin')
def delete_lot_api(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check for any active reservations in this lot, which is a more robust check
    active_reservations = Reservation.query.join(ParkingSpot).filter(
        ParkingSpot.lot_id == lot_id, 
        Reservation.leaving_timestamp == None
    ).count()

    if active_reservations > 0:
        return jsonify(msg="Cannot delete lot with active reservations"), 400

    # If no active reservations, proceed with deletion
    try:
        # Delete associated reservations first
        spot_ids = [spot.id for spot in lot.spots]
        Reservation.query.filter(Reservation.spot_id.in_(spot_ids)).delete(synchronize_session=False)

        # Delete associated spots
        ParkingSpot.query.filter_by(lot_id=lot_id).delete(synchronize_session=False)

        # Finally, delete the lot
        db.session.delete(lot)
        db.session.commit()
        return jsonify(msg="Lot and all associated data deleted successfully"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(msg=f"Error deleting lot: {str(e)}"), 500

@admin_bp.route('/api/lots', methods=['POST'])
@role_required('admin')
def create_lot():
    try:
        data = request.get_json()
        if not data:
            return jsonify(msg="No data provided"), 400
        
        # Validate required fields
        required_fields = ['name', 'price', 'address', 'pincode', 'spots']
        for field in required_fields:
            if field not in data:
                return jsonify(msg=f"Missing required field: {field}"), 400
        
        # Convert spots to integer
        try:
            spots = int(data['spots'])
            price = float(data['price'])
        except (ValueError, TypeError):
            return jsonify(msg="Invalid price or spots value"), 400
        
        lot = ParkingLot(
            prime_location_name=data['name'],
            price_per_hour=price,
            address=data['address'],
            pin_code=data['pincode'],
            number_of_spots=spots
        )
        db.session.add(lot)
        db.session.flush()

        for _ in range(spots):
            db.session.add(ParkingSpot(lot_id=lot.id))
        db.session.commit()
        return jsonify(msg="Created"), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(msg=f"Error creating lot: {str(e)}"), 500

@admin_bp.route('/api/admin/users', methods=['GET'])
@role_required('admin')
def list_users():
    users = User.query.all()
    return jsonify([
        {"id": u.id, "email": u.email, "name": u.full_name, "is_active": u.is_active}
        for u in users
    ])

@admin_bp.route('/api/admin/user-details/<int:user_id>', methods=['GET'])
@role_required('admin')
def get_user_details(user_id):
    user = User.query.get_or_404(user_id)
    
    # Get user's reservation statistics
    total_reservations = Reservation.query.filter_by(user_id=user_id).count()
    completed_reservations = Reservation.query.filter_by(
        user_id=user_id
    ).filter(Reservation.leaving_timestamp.isnot(None)).count()
    
    total_spent = db.session.query(func.sum(Reservation.parking_cost)).filter_by(
        user_id=user_id
    ).scalar() or 0
    
    # Get recent reservations
    recent_reservations = Reservation.query.filter_by(user_id=user_id).join(
        ParkingSpot
    ).join(ParkingLot).order_by(Reservation.parking_timestamp.desc()).limit(10).all()
    
    reservations_data = []
    for res in recent_reservations:
        reservations_data.append({
            "id": res.id,
            "lot_name": res.spot.lot.prime_location_name,
            "spot_id": res.spot_id,
            "start_time": res.parking_timestamp.strftime("%Y-%m-%d %H:%M"),
            "end_time": res.leaving_timestamp.strftime("%Y-%m-%d %H:%M") if res.leaving_timestamp else None,
            "cost": res.parking_cost,
            "status": "Completed" if res.leaving_timestamp else "Active"
        })
    
    return jsonify({
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.full_name,
            "is_active": user.is_active
        },
        "stats": {
            "total_reservations": total_reservations,
            "completed_reservations": completed_reservations,
            "total_spent": float(total_spent)
        },
        "recent_reservations": reservations_data
    })

@admin_bp.route('/api/admin/block-user/<int:user_id>', methods=['POST'])
@role_required('admin')
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Check if user has active reservations when trying to block
    if user.is_active:  # Only check when blocking, not unblocking
        active_reservations = Reservation.query.filter_by(
            user_id=user_id,
            leaving_timestamp=None
        ).count()
        
        if active_reservations > 0:
            return jsonify(msg="Cannot block user with active reservations. Please ask them to release their spots first."), 400
    
    # Toggle user active status
    user.is_active = not user.is_active
    db.session.commit()
    
    action = "unblocked" if user.is_active else "blocked"
    return jsonify(msg=f"User {action} successfully"), 200

@admin_bp.route('/api/admin/dashboard-stats', methods=['GET'])
@role_required('admin')
@cache.cached(timeout=300)  # Cache for 5 minutes
def dashboard_stats():
    try:
        # Total statistics
        total_lots = db.session.query(func.count(ParkingLot.id)).scalar()
        total_spots = db.session.query(func.count(ParkingSpot.id)).scalar()
        occupied_spots = db.session.query(func.count(ParkingSpot.id)).filter(ParkingSpot.status == 'O').scalar()
        available_spots = total_spots - occupied_spots
        total_users = db.session.query(func.count(User.id)).scalar()
        
        # Recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_reservations = db.session.query(func.count(Reservation.id)).filter(
            Reservation.parking_timestamp >= yesterday
        ).scalar()
        
        # Revenue today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_revenue = db.session.query(func.sum(Reservation.parking_cost)).filter(
            Reservation.leaving_timestamp >= today_start
        ).scalar() or 0
        
        # Most popular parking lot
        popular_lot_query = db.session.query(
            ParkingLot.prime_location_name,
            func.count(Reservation.id).label('reservation_count')
        ).select_from(Reservation).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            ParkingLot, ParkingSpot.lot_id == ParkingLot.id
        ).group_by(ParkingLot.prime_location_name).order_by(func.count(Reservation.id).desc())

        popular_lot = popular_lot_query.first()
        
        return jsonify({
            "total_lots": total_lots,
            "total_spots": total_spots,
            "occupied_spots": occupied_spots,
            "available_spots": available_spots,
            "total_users": total_users,
            "recent_reservations": recent_reservations,
            "today_revenue": float(today_revenue),
            "most_popular_lot": popular_lot[0] if popular_lot else "None"
        })
    except Exception as e:
        return jsonify(msg=f"Error in dashboard_stats: {str(e)}"), 500

@admin_bp.route('/api/admin/lot-details/<int:lot_id>', methods=['GET'])
@role_required('admin')
def lot_details(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    
    spot_details = []
    for spot in spots:
        active_reservation = Reservation.query.filter_by(
            spot_id=spot.id, 
            leaving_timestamp=None
        ).first()
        
        spot_details.append({
            "id": spot.id,
            "status": spot.status,
            "occupied_by": active_reservation.user.email if active_reservation else None,
            "parking_since": active_reservation.parking_timestamp.strftime("%Y-%m-%d %H:%M") if active_reservation else None
        })
    
    return jsonify({
        "lot": {
            "id": lot.id,
            "name": lot.prime_location_name,
            "price_per_hour": lot.price_per_hour,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "total_spots": lot.number_of_spots
        },
        "spots": spot_details
    })

@admin_bp.route('/api/admin/edit-lot/<int:lot_id>', methods=['PUT'])
@role_required('admin')
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    data = request.get_json()
    
    # Check if we can reduce spots (no occupied spots in excess)
    current_occupied = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
    new_spot_count = data.get('spots', lot.number_of_spots)
    
    if new_spot_count < current_occupied:
        return jsonify(msg="Cannot reduce spots below currently occupied count"), 400
    
    # Update lot details
    lot.prime_location_name = data.get('name', lot.prime_location_name)
    lot.price_per_hour = data.get('price', lot.price_per_hour)
    lot.address = data.get('address', lot.address)
    lot.pin_code = data.get('pincode', lot.pin_code)
    
    # Handle spot count changes
    if new_spot_count != lot.number_of_spots:
        current_spots = ParkingSpot.query.filter_by(lot_id=lot_id).count()
        
        if new_spot_count > current_spots:
            # Add more spots
            for _ in range(new_spot_count - current_spots):
                new_spot = ParkingSpot(lot_id=lot_id)
                db.session.add(new_spot)
        else:
            # Remove excess available spots
            available_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').limit(
                current_spots - new_spot_count
            ).all()
            for spot in available_spots:
                db.session.delete(spot)
        
        lot.number_of_spots = new_spot_count
    
    db.session.commit()
    return jsonify(msg="Lot updated successfully"), 200
