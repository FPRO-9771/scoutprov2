import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')

    # Database — Heroku uses postgres://, SQLAlchemy needs postgresql://
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///scoutpro.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # The Blue Alliance API
    TBA_API_KEY = os.environ.get('TBA_API_KEY')

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = FLASK_ENV == 'production'
