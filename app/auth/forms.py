import time

import validators as valid_package

from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import validators, StringField, EmailField, PasswordField, RadioField
from wtforms.validators import DataRequired, ValidationError

from app import db
from app.auth.form_errors import LoginFormErrors, RegistrationFormError
from app.auth.helpers import log_failure
from app.models.user import User
from app.shared.general_form_error_enum import GeneralFormError
from app.shared.shared import breached_password_validator


class RegistrationForm(FlaskForm):
    """
    A class to represents the input fields for registering a new user for this application

    Fields
    -----------
    account_type: radio
        The type of account to be created. Admin or regular
    email: email
        The email address of the user signing up for the account
    first_name: text
        The first name of the person signing up for the account
    last_name: text
        The last name of the person signing up for the account
    password: password
        The password used to sign to the created account
    confirm_password: password
        Confirm the password used to sign to the account
    """
    account_type = RadioField('Select Account Type:',[DataRequired()], choices=[('admin','Admin'),('regular','Regular')])
    email = EmailField('Email', [DataRequired(), validators.Length(max=150, message=GeneralFormError.INVALID_EMAIL_LENGTH.value)])
    first_name = StringField('First Name', [DataRequired(), validators.Length(min=2, max=150, message=RegistrationFormError.INVALID_FIRST_NAME_LENGTH.value),
                                            validators.Regexp('^[A-Za-z-]+$', message=RegistrationFormError.INVALID_FIRST_NAME_FORMAT.value)])
    last_name = StringField('Last Name', [DataRequired(), validators.Length(min=2, max=150, message= RegistrationFormError.INVALID_LAST_NAME_LENGTH.value),
                                          validators.Regexp('^[A-Za-z-]+$', message=RegistrationFormError.INVALID_LAST_NAME_FORMAT.value)])
    password = PasswordField('Password', [DataRequired(),
                                          validators.Regexp(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*_+])[A-Za-z\d!@#$%^&*_+]{7,20}$', message=RegistrationFormError.PASSWORD_DOES_NOT_MEET_REQUIREMENTS.value),
                                          validators.Length(min=7, max=20, message=RegistrationFormError.INVALID_PASSWORD_LENGTH.value), validators.EqualTo('confirm_password', message=RegistrationFormError.PASSWORDS_DO_NOT_MATCH.value), breached_password_validator])
    confirm_password = PasswordField('Confirm Password', [DataRequired(), validators.Length(min=7, max=20, message=RegistrationFormError.INVALID_PASSWORD_LENGTH.value), validators.EqualTo('password', message=RegistrationFormError.PASSWORDS_DO_NOT_MATCH.value), breached_password_validator])


    def validate_email(self, field):
        """Checks if the email address is valid using the validators package and if there is already an account with the same email address"""
        user = User.find_user_by_email(field.data)

        if user:
            raise ValidationError(RegistrationFormError.EMAIL_EXISTS.value)

        if not valid_package.email(field.data):
            raise ValidationError(GeneralFormError.INVALID_EMAIL.value)

class LoginForm(FlaskForm):
    """
    A class to represents the input fields for signing in to the application

    Fields
    -------------
    email: email
        The email address for the account
    password: password
        The password linked to the email address used to sign in to the account
    """
    login_email = EmailField('Email', [DataRequired()])
    login_password = PasswordField('Password', [DataRequired()])

    def validate_login_password(self, field):
        """Checks if the password entered in correct for the corresponding email address in the database"""

        user = User.find_user_by_email(self.login_email.data)

        if user.failed_attempts > 0:
            delay = min(2 ** user.failed_attempts, 8)
            time.sleep(delay)

        if check_password_hash(user.password, field.data):
            user.failed_attempts = 0
            db.session.commit()
        elif user and not check_password_hash(user.password, field.data):
            user.failed_attempts += 1
            log_failure(self.login_email.data, LoginFormErrors.INCORRECT_PASSWORD.value)
            db.session.commit()
            raise ValidationError(LoginFormErrors.INCORRECT_EMAIL_OR_PASSWORD.value)

class ForgotPasswordForm(FlaskForm):
    email = EmailField('Email', [DataRequired(),
                                 validators.Length(max=150, message=GeneralFormError.INVALID_EMAIL_LENGTH.value)])



class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', [DataRequired(),
                                          validators.Regexp(
                                              r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*_+])[A-Za-z\d!@#$%^&*_+]{7,20}$',
                                              message=RegistrationFormError.PASSWORD_DOES_NOT_MEET_REQUIREMENTS.value),
                                          validators.Length(min=7, max=20,
                                                            message=RegistrationFormError.INVALID_PASSWORD_LENGTH.value),
                                          validators.EqualTo('confirm_password',
                                                             message=RegistrationFormError.PASSWORDS_DO_NOT_MATCH.value),
                                          breached_password_validator])
    confirm_password = PasswordField('Confirm Password', [DataRequired(), validators.Length(min=7, max=20,
                                                                                            message=RegistrationFormError.INVALID_PASSWORD_LENGTH.value),
                                                          validators.EqualTo('password',
                                                                             message=RegistrationFormError.PASSWORDS_DO_NOT_MATCH.value),
                                                          breached_password_validator])