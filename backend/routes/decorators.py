from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps
from flask import jsonify

def role_required(required_role):
    """
    Decorator to protect endpoints so that only tokens
    with JWT claim "role" == required_role may access.
    """
    def wrapper_fn(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != required_role:
                return jsonify(msg="Forbidden: insufficient privileges"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper_fn
