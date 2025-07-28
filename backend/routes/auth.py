from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
<<<<<<< HEAD
from extensions import db
from models import User, Admin
=======
from ..extensions import db
from ..models import User, Admin
>>>>>>> fa507b6 (Amped up UI and milestone 6 implemented)
from .decorators import role_required

auth_bp = Blueprint('auth', __name__)

# ─── User Registration ─────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email    = data.get('email')
    password = data.get('password')
    full_name= data.get('full_name')

    if not email or not password:
        return jsonify(msg="email and password required"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(msg="email already registered"), 400

    u = User(email=email, full_name=full_name)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()

    return jsonify(msg="user registered"), 201


# ─── User Login ────────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email    = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify(msg="bad credentials"), 401

    additional_claims = {"role": "user"}
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    return jsonify(access_token=access_token), 200


# ─── Admin Login ───────────────────────────────────────────────────────────────
@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    admin = Admin.query.filter_by(username=username).first()
    if not admin or not admin.check_password(password):
        return jsonify(msg="bad credentials"), 401

    claims = {"role": "admin"}
    token = create_access_token(identity=str(admin.id), additional_claims=claims)
    return jsonify(access_token=token), 200


# ─── Example Protected Route ─────────────────────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def who_am_i():
    """
    Returns the JWT identity and role—good as a quick smoke‑test.
    """
    user_id = get_jwt_identity()
    role    = get_jwt().get('role')
    return jsonify(logged_in_as=user_id, role=role), 200

@auth_bp.route('/reserve-example', methods=['POST'])
@role_required('user')
def example_reserve():
    # You know by now this will only run for a valid "user" token
    return jsonify(msg="User may reserve."), 200

# Example: an admin-only route
@auth_bp.route('/lot-example', methods=['POST'])
@role_required('admin')
def example_create_lot():
    return jsonify(msg="Admin may create a lot."), 200