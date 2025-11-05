import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-min-32-characters'
    
    # Railway/Heroku fix: DATABASE_URL might use postgres:// instead of postgresql://
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///marketplace.db'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'app/static/images/products'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 5242880)
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    ITEMS_PER_PAGE = 20
    
    MOCK_PAYMENT_ENABLED = True
    MOCK_SMS_ENABLED = True
    MOCK_DRIVER_TRACKING = True
    MOCK_EMAIL_ENABLED = True
    
    CREDIT_TIERS = {
        'bronze': (0, 250),
        'silver': (251, 500),
        'gold': (501, 750),
        'platinum': (751, 1000)
    }

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Railway handles HTTPS but we need to be more permissive with sessions
    SESSION_COOKIE_SECURE = False  # Railway proxy handles HTTPS
    SESSION_COOKIE_SAMESITE = None  # More permissive for Railway

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
