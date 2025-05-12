import os
from pathlib import Path

import app


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///telehealth.db'
    SQLALCHEMY_DATABASE_URI = 'postgresql://kmchealth:qH1ERWF4dKc08dOoZ3YdCExaDgW3Q3Ah@dpg-d04vaip5pdvs73afpqpg-a.virginia-postgres.render.com/telehealthdb1'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = False
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_COOKIE_SECURE = True  # Set to True in production (for HTTPS connections)
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/token/refresh'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')
    env_file = ".env"
    case_sensitive = True
    from_attributes = True
  
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    EXPORT_FOLDER = str(BASE_DIR / "exports")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    @staticmethod
    def init_app(app):
        Path(Config.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(Config.EXPORT_FOLDER).mkdir(parents=True, exist_ok=True)

    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

settings = Config()