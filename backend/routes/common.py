from flask import Blueprint, jsonify
from models import ParkingLot
from extensions import db
from flask_jwt_extended import jwt_required

common_bp = Blueprint('common', __name__)

@common_bp.route('/api/lots', methods=['GET'])
@jwt_required()
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
