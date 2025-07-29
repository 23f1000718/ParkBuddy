import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, '..', 'parkbuddy.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'SECRET1')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'SECRET2')  
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = REDIS_URL  # Flask-Caching
    
    # Celery Configuration
    # Flask-Mail config for Mailhog
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 1025))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', None)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'parkbuddy@localhost')

    # Celery Configuration (modern, lowercase)
    CELERY_CONFIG = {
        'broker_url': os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        'result_backend': os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        'imports': ('backend.tasks',),
        'beat_schedule': {
            'daily-reminders': {
                'task': 'backend.tasks.send_daily_reminders',
                'schedule': 60.0,  # Every 1 minute for demo
            },
            'monthly-reports': {
                'task': 'backend.tasks.send_monthly_reports',
                'schedule': 120.0,  # Every 2 minutes for demo
            },
        },
        'timezone': 'UTC',
    }