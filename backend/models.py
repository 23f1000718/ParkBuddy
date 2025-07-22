from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd_hash = db.Column(db.String(128), nullable=False)
    full_name= db.Column(db.String(100))
    reservations = db.relationship('Reservation', back_populates='user')

    def set_password(self, pw):
        self.pwd_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.pwd_hash, pw)


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    pwd_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, pw):
        self.pwd_hash = generate_password_hash(pw)


class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name  = db.Column(db.String(100), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200))
    pin_code = db.Column(db.String(20))
    number_of_spots = db.Column(db.Integer, nullable=False)
    spots = db.relationship('ParkingSpot', back_populates='lot', cascade='all, delete-orphan')


class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    id = db.Column(db.Integer, primary_key=True)
    lot_id  = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status  = db.Column(db.String(1), default='A', nullable=False)

    lot = db.relationship('ParkingLot', back_populates='spots')
    reservations = db.relationship('Reservation', back_populates='spot', cascade='all, delete-orphan')


class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost      = db.Column(db.Float, nullable=True)

    spot = db.relationship('ParkingSpot', back_populates='reservations')
    user = db.relationship('User', back_populates='reservations')
