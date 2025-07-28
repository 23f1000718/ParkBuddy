import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, '..', 'parkbuddy.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'SECRET1')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'SECRET2')  
    JWT_ACCESS_TOKEN_EXPIRES = 3600  