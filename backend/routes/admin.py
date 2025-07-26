from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, ParkingLot, ParkingSpot
from extensions import db
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

    for _ in range(data['spots']):
        db.session.add(ParkingSpot(lot_id=lot.id))
    db.session.commit()
    return jsonify(msg="Created"), 201

@admin_bp.route('/api/admin/users', methods=['GET'])
@role_required('admin')
def list_users():
    users = User.query.all()
    return jsonify([
        {"id": u.id, "email": u.email, "name": u.full_name}
        for u in users
    ])

