import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Basic Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///bariatric.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MongoDB Configuration
    MONGODB_SETTINGS = {
        'host': os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bariatric'),
        'db': os.getenv('MONGODB_DB', 'bariatric'),
        'username': os.getenv('MONGODB_USERNAME'),
        'password': os.getenv('MONGODB_PASSWORD')
    }
    
    # Database Selection
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'postgresql')  # or 'mongodb'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Mail Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Security Configuration
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'your-security-password-salt')
    
    # Role Configuration
    ADMIN_ROLES = ['super_admin', 'admin']
    MEDICAL_ROLES = ['doctor', 'nurse']
    STAFF_ROLES = ['staff', 'receptionist']
    
    # Pagination
    ITEMS_PER_PAGE = 10
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///bariatric.db')
    
    # Disable email temporarily
    MAIL_ENABLED = os.getenv('MAIL_ENABLED', 'False').lower() == 'true'
    
    # Disable Redis/Celery temporarily
    REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'False').lower() == 'true'

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bariatric_test.db'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
