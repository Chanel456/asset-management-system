from dotenv import load_dotenv
import secrets
import os

DB_NAME = 'database.db'

load_dotenv('/home/Chanelj/asset-management-system/.env')

class ProdConfig:
    TESTING = False
    SECRET_KEY = secrets.token_urlsafe(24)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = 0
    SESSION_PERMANENT = False
    SESSION_TYPE = 'sqlalchemy'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')