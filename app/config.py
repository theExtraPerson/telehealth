import os
from pathlib import Path
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration with default settings"""
    
    # Core Application Settings
    SECRET_KEY = os.getenv('SECRET_KEY', Fernet.generate_key().decode())
    APP_NAME = "Telehealth System"
    VERSION = "1.0.0"
    ENV = os.getenv('FLASK_ENV', 'development')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 
        'mssql+pyodbc://kmchealth:h34lth@KMC-HEALTH\\SQLEXPRESS/HealthDB?driver=ODBC+Driver+17+for+SQL+Server')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_size': 10,
        'max_overflow': 5
    }

    # Security & Authentication
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 604800))  # 7 days
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_COOKIE_SECURE = os.getenv('JWT_COOKIE_SECURE', 'False').lower() == 'true'
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/token/refresh'
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', SECRET_KEY)

    # File Storage
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    EXPORT_FOLDER = str(BASE_DIR / "exports")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'dicom'}

    # Encryption Settings
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY') or Fernet.generate_key().decode()
    ENCRYPTION_ALGORITHM = 'FERNET'  # Options: FERNET, AES
    SENSITIVE_FIELDS = ['description', 'diagnosis', 'treatment', 'medications', 'allergies', 'vital_signs']

    # Telemedicine Settings
    TELEMEDICINE_BASE_URL = os.getenv('TELEMEDICINE_BASE_URL', 'https://telemed.example.com')
    TELEMEDICINE_SESSION_DURATION = 60  # minutes
    TELEMEDICINE_PROVIDERS = ['zoom', 'teams', 'custom']

    # Audit Logging
    AUDIT_LOG_ENABLED = True
    AUDIT_LOG_FILE = str(BASE_DIR / "logs" / "audit.log")
    AUDIT_LOG_RETENTION = 365  # days

    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@telehealth.example.com')

    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Ensure directories exist
        required_dirs = [
            Config.UPLOAD_FOLDER,
            Config.EXPORT_FOLDER,
            os.path.dirname(Config.AUDIT_LOG_FILE)
        ]
        for directory in required_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)

        # Configure logging
        if Config.AUDIT_LOG_ENABLED:
            import logging
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                Config.AUDIT_LOG_FILE,
                maxBytes=1024 * 1024 * 10,  # 10 MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Telehealth application startup')
    
    @staticmethod
    def validate_encryption_key():
        """Validate the encryption key format"""
        try:
            from cryptography.fernet import Fernet
            Fernet(Config.ENCRYPTION_KEY.encode())
            return True
        except ValueError:
            return False
        
        
class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    JWT_COOKIE_SECURE = False  # Allow non-HTTPS in development
    ENCRYPTION_KEY = 'development-key-not-secure'  # Override for development

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    ENCRYPTION_KEY = 'testing-key-not-secure'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    JWT_COOKIE_SECURE = True
    SQLALCHEMY_ECHO = False
    AUDIT_LOG_ENABLED = True

    @classmethod
    def check_security(cls):
        """Verify production security settings"""
        if cls.ENCRYPTION_KEY == cls.SECRET_KEY:
            raise ValueError("Encryption key should not match secret key in production")
        if 'dev' in cls.ENCRYPTION_KEY.lower():
            raise ValueError("Development encryption key detected in production")

# Configuration selector
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Current settings based on environment
settings = ProductionConfig() if Config.ENV == 'production' else DevelopmentConfig()
if Config.ENV == 'production':
    ProductionConfig.check_security()