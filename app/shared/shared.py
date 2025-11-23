import hashlib

import requests
from flask import current_app
from flask_mail import Message
from wtforms.validators import ValidationError

from app.auth.form_errors import RegistrationFormError
from app.extensions import mail

def breached_password_validator(field):
    password = field.data
    hashed_pass = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = hashed_pass[:5], hashed_pass[5:]
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


def send_email(subject, recipients, body, html=None):
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
