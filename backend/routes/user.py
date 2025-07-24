from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import get_jwt_identity
from models import ParkingLot, ParkingSpot, Reservation, User
from app import db
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
