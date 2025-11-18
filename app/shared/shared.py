import hashlib
import logging
from enum import Enum

import requests
from flask import request, current_app, url_for, flash, redirect
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from wtforms.validators import ValidationError

from app.auth.form_errors import RegistrationFormError
from app.extensions import mail
from app.models.user import User


class FormType(Enum):
    CREATE = 'Create'
    UPDATE = 'Update'

class GeneralFormError(Enum):
    INVALID_URL = 'Please enter a valid URL'
    INVALID_EMAIL = 'Please enter a valid email'
    INVALID_EMAIL_LENGTH = 'Email address cannot exceed 150 characters'
    INTEGER_NOT_GREATER_THAN_OR_EQUAL_TO_ZERO= 'Please enter a valid integer greater than 0'
    INTEGER_NOT_GREATER_THAN_OR_EQUAL_TO_ONE = 'Please enter a valid integer greater than 1'

class Utils:
    def breached_password_validator(self, field):
        password = field.data
        hashed_pass = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = hashed_pass[:5], hashed_pass[5:]
        #TODO:  add this url to a config map somewhere
        url = f'https://api.pwnedpasswords.com/range/{prefix}'
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                raise ValidationError(RegistrationFormError.PASSWORD_CHECK_FAILED.value)
            hashes = (line.split(':') for line in response.text.splitlines())
            if any(s == suffix for s, count in hashes):
                raise ValidationError(RegistrationFormError.WEAK_PASSWORD.value)
        except requests.RequestException:
            raise ValidationError(RegistrationFormError.PASSWORD_SAFETY.value)

    @staticmethod
    def log_failure(email, reason):
        logging.warning(
            f'Login failure | email={email} | ip={request.remote_addr} '
            f'| user_agent={request.user_agent.string} | reason={reason}'
        )

    @staticmethod
    def generate_reset_token(user):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        logging.info(user.password)
        return serializer.dumps(
            {'email': user.email, 'pw_hash': user.password},
            salt='password-reset'
        )

    @staticmethod
    def verify_reset_token(token, expiration=3600):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token, salt='password-reset', max_age=3600)
        except Exception as e:
            logging.error(f'Invalid or expired reset token: {e}')
            return redirect(url_for('auth.forgot'))

        email = data.get("email")
        pw_hash = data.get("pw_hash")

        user = User.find_user_by_email(email)
        if not user:
            logging.error('Reset token refers to unknown user.')
            return redirect(url_for('auth.forgot'))

        # Invalidate token automatically if password was changed
        if pw_hash != user.password:
            flash('Reset token invalidated because password has changed.', category='error')
            return redirect(url_for('auth.forgot'))

        return email

    @staticmethod
    def send_email(subject, recipients, body, html):
        """
            Generic email sending function.
            Works with Flask application factory and Flask-Mail.
            """
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
            html=html,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        mail.send(msg)

    @staticmethod
    def send_password_reset_email(user):
        """
        Sends the password reset email to a user.
        """
        token = Utils.generate_reset_token(user)

        reset_url = url_for("auth.reset", token=token, _external=True)
        logging.info(reset_url)

        subject = 'Password Reset Request'
        body = f'To reset your password, click the following link:\n{reset_url}'
        html = f"<p>To reset your password, click the following link:</p><p><a href='{reset_url}'>{reset_url}</a></p>"

        Utils.send_email(subject, [user.email], body, html)