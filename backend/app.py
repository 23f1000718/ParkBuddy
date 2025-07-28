from flask import Flask, send_from_directory
from .extensions import db, jwt, cache, make_celery
from .config import Config
from flask_mail import Mail
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
<<<<<<< HEAD
=======
    cache.init_app(app)
    
    # Initialize mail
    mail = Mail()
    mail.init_app(app)
    
    # Register blueprints
    from .routes.admin import admin_bp
    from .routes.user import user_bp
    from .routes.auth import auth_bp
    from .routes.common import common_bp
>>>>>>> fa507b6 (Amped up UI and milestone 6 implemented)
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(common_bp, url_prefix='/api')

    # Add static file routes
    @app.route('/')
    def index():
        return send_from_directory('..', 'index.html')

    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory('..', path)

    return app

<<<<<<< HEAD
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
=======
app = create_app()
celery = make_celery(app)
>>>>>>> fa507b6 (Amped up UI and milestone 6 implemented)
