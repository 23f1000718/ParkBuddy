from flask import Flask
from extensions import db, jwt
from config import Config
from routes.admin import admin_bp
from routes.user import user_bp
from routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    return app
