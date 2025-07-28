from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import get_jwt_identity
from ..models import ParkingLot, ParkingSpot, Reservation, User
from ..extensions import db
from .decorators import role_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/dashboard')
@role_required('user')
def user_dashboard():
    lots = ParkingLot.query.all()
    return render_template('user_dashboard.html', lots=lots)


@user_bp.route('/user/reserve/<int:lot_id>', methods=['GET', 'POST'])
@role_required('user')
def reserve(lot_id):
    if request.method == 'POST':
        user_id = get_jwt_identity()
        spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not spot:
            flash("No available spots")
            return redirect(url_for('user.user_dashboard'))

        # reserve spot
        spot.status = 'O'
        res = Reservation(spot_id=spot.id, user_id=user_id)
        db.session.add(res)
        db.session.commit()
        flash("Spot reserved!")
        return redirect(url_for('user.user_dashboard'))

    return render_template('reserve.html', lot_id=lot_id)

@user_bp.route('/api/user/reserve/<int:lot_id>', methods=['POST'])
@role_required('user')
def reserve_api(lot_id):
    user_id = get_jwt_identity()
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
def release_api(res_id):
    from datetime import datetime
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
def reservations_history():
    user_id = get_jwt_identity()
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            "spot_id": res.spot_id,
            "lot": res.spot.lot.prime_location_name,
            "start": res.parking_timestamp.strftime("%Y-%m-%d %H:%M"),
            "end": res.leaving_timestamp.strftime("%Y-%m-%d %H:%M") if res.leaving_timestamp else None,
            "cost": res.parking_cost
        }
        for res in reservations
    ])
