from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
<<<<<<< HEAD
from models import User, ParkingLot, ParkingSpot
from extensions import db
=======
from ..models import User, ParkingLot, ParkingSpot, Reservation
from ..extensions import db, cache
>>>>>>> fa507b6 (Amped up UI and milestone 6 implemented)
from .decorators import role_required
from datetime import datetime, timedelta

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

@admin_bp.route('/api/admin/lots/<int:lot_id>', methods=['DELETE'])
@role_required('admin')
def delete_lot_api(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
    if occupied > 0:
        return jsonify(msg="Cannot delete lot with occupied spots"), 400

    db.session.delete(lot)
    db.session.commit()
    return jsonify(msg="Deleted"), 200

@admin_bp.route('/api/admin/lots', methods=['POST'])
@role_required('admin')
<<<<<<< HEAD
def create_lot_api():
    data = request.get_json()
    lot = ParkingLot(
        prime_location_name=data['name'],
        price_per_hour=data['price'],
        address=data['address'],
        pin_code=data['pincode'],
        number_of_spots=data['spots']
    )
    db.session.add(lot)
    db.session.flush()
=======
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
>>>>>>> fa507b6 (Amped up UI and milestone 6 implemented)

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
        {"id": u.id, "email": u.email, "name": u.full_name}
        for u in users
    ])

@admin_bp.route('/api/admin/dashboard-stats', methods=['GET'])
@role_required('admin')
@cache.cached(timeout=300)  # Cache for 5 minutes
def dashboard_stats():
    # Total statistics
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    available_spots = total_spots - occupied_spots
    total_users = User.query.count()
    
    # Recent activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_reservations = Reservation.query.filter(
        Reservation.parking_timestamp >= yesterday
    ).count()
    
    # Revenue today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue = db.session.query(db.func.sum(Reservation.parking_cost)).filter(
        Reservation.leaving_timestamp >= today_start
    ).scalar() or 0
    
    # Most popular parking lot
    popular_lot = db.session.query(
        ParkingLot.prime_location_name,
        db.func.count(Reservation.id)
    ).join(ParkingSpot).join(Reservation).group_by(
        ParkingLot.prime_location_name
    ).order_by(db.func.count(Reservation.id).desc()).first()
    
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

