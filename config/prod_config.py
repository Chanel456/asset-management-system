import secrets

DB_NAME = 'database.db'

class ProdConfig:
    TESTING = False
    SECRET_KEY = secrets.token_urlsafe(24)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = 0
    SESSION_PERMANENT = False
    SESSION_TYPE = 'sqlalchemy'
    MAIL_SERVER = 'smtp.pythonanywhere.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'noreply@pythonanywhere.com'