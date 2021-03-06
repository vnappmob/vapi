"""vauth/app/config.py"""
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    """BaseConfig"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vapi'
    VPRICE_FCM_KEY = os.environ.get('VPRICE_FCM_KEY') or 'vapi'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_CONFIG = {
        'db_host': 'db',
        'db_user': 'root',
        'db_password': '123456',
        'db_port': 3306
    }
    MONGODB_CONFIG = {
        'db_host': os.environ.get('MONGODB_HOST') or '',
        'db_user': os.environ.get('MONGODB_USER') or '',
        'db_password': os.environ.get('MONGODB_PASSWORD') or '',
        'db_port': os.environ.get('MONGODB_PORT') or '27017'
    }


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    DATABASE_CONFIG = {
        'db_host': os.environ.get('DB_HOST') or '',
        'db_user': os.environ.get('DB_USER') or '',
        'db_password': os.environ.get('DB_PASSWORD') or '',
        'db_port': 3306
    }
    MONGODB_CONFIG = {
        'db_host': os.environ.get('MONGODB_HOST') or '',
        'db_user': os.environ.get('MONGODB_USER') or '',
        'db_password': os.environ.get('MONGODB_PASSWORD') or '',
        'db_port': os.environ.get('MONGODB_PORT') or '27017'
    }
