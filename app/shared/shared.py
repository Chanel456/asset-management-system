import hashlib
import logging
from enum import Enum

import requests
from flask import request
from wtforms.validators import ValidationError

from app.auth.form_errors import RegistrationFormError

class FormType(Enum):
    CREATE = "Create"
    UPDATE = "Update"

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
            f"Login failure | email={email} | ip={request.remote_addr} "
            f"| user_agent={request.user_agent.string} | reason={reason}"
        )

