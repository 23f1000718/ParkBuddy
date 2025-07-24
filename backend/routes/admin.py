from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import ParkingLot, ParkingSpot
from app import db
from .decorators import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    lots = ParkingLot.query.all()
    return render_template('admin_dashboard.html', lots=lots)


@admin_bp.route('/admin/add-lot', methods=['GET', 'POST'])
@role_required('admin')
def add_lot():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        address = request.form['address']
        pincode = request.form['pincode']
        spot_count = int(request.form['spots'])

        lot = ParkingLot(
            prime_location_name=name,
            price_per_hour=price,
            address=address,
            pin_code=pincode,
            number_of_spots=spot_count
        )
        db.session.add(lot)
        db.session.flush()  # generate lot.id

        # auto-create spots
        for _ in range(spot_count):
            spot = ParkingSpot(lot_id=lot.id)
            db.session.add(spot)

        db.session.commit()
        flash("Parking lot created")
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('add_lot.html')


@admin_bp.route('/admin/delete-lot/<int:lot_id>', methods=['POST'])
@role_required('admin')
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    db.session.delete(lot)
    db.session.commit()
    flash("Lot deleted")
    return redirect(url_for('admin.admin_dashboard'))
