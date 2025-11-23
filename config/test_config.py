import secrets

class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    WTF_CSRF_CHECK_DEFAULT = False
    SECRET_KEY = secrets.token_urlsafe(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SESSION_SQLALCHEMY = None
    SESSION_SQLALCHEMY_TABLE = 'test_sessions'