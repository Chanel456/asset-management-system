import logging
import time
from datetime import timedelta, datetime

from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError

from app import db

class FailedLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True)
    ip = db.Column(db.String(45), index=True)
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, index=True, nullable=False, server_default=db.func.now())

    WINDOW = timedelta(minutes=5)
    ACCOUNT_FAIL_THRESHOLD = 5
    IP_FAIL_THRESHOLD = 30
    GLOBAL_FAIL_THRESHOLD = 500

    @staticmethod
    def record_failed_login(email, ip, user_agent):
        try:
            failed_login = FailedLogin(email=email, ip=ip, user_agent=user_agent)
            db.session.add(failed_login)
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            logging.error('An error was encountered when saving failed login attempt for email: %s', email)
            logging.error(err)

    @staticmethod
    def recent_failures_for_email(email):
        since = datetime.utcnow() - FailedLogin.WINDOW
        return FailedLogin.query.filter(FailedLogin.email == email,
                                        FailedLogin.created_at >= since).count()

    @staticmethod
    def recent_failures_for_ip(ip):
        since = datetime.utcnow() - FailedLogin.WINDOW
        return FailedLogin.query.filter(FailedLogin.ip == ip,
                                        FailedLogin.created_at >= since).count()

    @staticmethod
    def recent_global_failures():
        since = datetime.utcnow() - FailedLogin.WINDOW
        return FailedLogin.query.filter(FailedLogin.created_at >= since).count()

    @staticmethod
    def apply_adaptive_friction(user, email, ip):
        # Base exponential backoff
        base_delay = min(2 ** user.failed_attempts, 8)

        # Add extra delay if suspicious
        if FailedLogin.recent_failures_for_ip(ip) >= FailedLogin.IP_FAIL_THRESHOLD:
            base_delay += 5
        if FailedLogin.recent_failures_for_email(email) >= FailedLogin.ACCOUNT_FAIL_THRESHOLD:
            base_delay += 5
        if FailedLogin.recent_global_failures() >= FailedLogin.GLOBAL_FAIL_THRESHOLD:
            base_delay += 10

        time.sleep(base_delay)

    @staticmethod
    def fetch_all_failed_logins():
        """Fetches all logins in the failed login table"""
        try:
            failed_logins = db.session.query(FailedLogin).all()
            return failed_logins
        except SQLAlchemyError as err:
            logging.error('An error occurred whilst fetching all rows in the failed login table')
            logging.error(err)

@event.listens_for(FailedLogin.__table__, 'after_create')
def create_failed_logins(*args, **kwargs):
    """Inserting 10 rows of data into the application table after database creation"""
    try:
        db.session.add(FailedLogin(email='failed_loginone@gmail.com', ip='192.84.17.203',
                                   user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'))
        db.session.add(FailedLogin(email='failed_logintwo@gmail.com', ip='203.45.67.89',
                                   user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'))
        db.session.add(FailedLogin(email='failed_loginthree@yahoo.com', ip='185.23.44.102',
                                   user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0'))
        db.session.add(FailedLogin(email='failed_loginfour@hotmail.com', ip='77.92.14.56',
                                   user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'))
        db.session.add(FailedLogin(email='failed_loginfive@outlook.com', ip='62.101.33.210',
                                   user_agent='Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36'))
        db.session.add(FailedLogin(email='failed_loginsix@gmail.com', ip='91.204.11.77',
                                   user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0'))
        db.session.add(FailedLogin(email='failed_loginseven@protonmail.com', ip='146.88.29.134',
                                   user_agent='curl/7.68.0'))
        db.session.add(FailedLogin(email='failed_logineight@gmail.com', ip='213.55.98.45',
                                   user_agent='python-requests/2.31.0'))
        db.session.add(FailedLogin(email='failed_loginnine@yahoo.com', ip='102.44.67.12',
                                   user_agent='Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'))
        db.session.add(FailedLogin(email='failed_loginten@hotmail.com', ip='54.23.198.77',
                                   user_agent='Mozilla/5.0 (Linux; Android 12; Samsung Galaxy S21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36'))
        db.session.commit()
    except SQLAlchemyError as err:
        db.session.rollback()
        logging.error('Unable to add dummy data to Failed table on database creation')
        logging.error(err)