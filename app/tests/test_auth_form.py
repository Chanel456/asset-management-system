import pytest
from wtforms.validators import ValidationError

from app.auth.forms import LoginForm, RegistrationForm


def test_password_validator_passes(init_user_table, app):
    with app.app_context():
        with app.test_request_context():
            form = LoginForm(data={'login_email': 'test.user1@gmail.com', 'login_password': '#Password12345'})
            form.validate_login_password(form.login_password)
            assert len(form.login_password.errors) == 0

def test_password_validator_fails(init_user_table, app):
    with app.app_context():
        with app.test_request_context():
            form = LoginForm(data = {'login_email': 'test.user1@gmail.com', 'login_password': '#Incorr£TPa$$word'})
            with pytest.raises(ValidationError):
                form.validate_login_password(form.login_password)

def test_email_validator_passes(app):
    with app.app_context():
        with app.test_request_context():
            form = RegistrationForm()
            form.email.data = 'test.user1@gmail.com'
            form.validate_email(form.email)
            assert len(form.email.errors) == 0

def test_email_validator_fails(app):
    with app.app_context():
        with app.test_request_context():
            form = RegistrationForm()
            form.email.data = 'test.user1@gmail'
            with pytest.raises(ValidationError):
                form.validate_email(form.email)

def test_registration_form_validation_passes(app):
    with app.app_context():
        with app.test_request_context():
            form = RegistrationForm(data={'account_type': 'regular', 'email': 'test.user1@gmail.com', 'first_name': 'Hello', 'last_name': "Williams", 'password': '#Password1234', 'confirm_password': '#Password1234'})
            assert form.validate() == True

def test_registration_form_validation_fails(app):
    with app.app_context():
        with app.test_request_context():
            form = RegistrationForm( data={'account_type': 'regular', 'email': 'test.user1@', 'first_name': 'Hello', 'last_name': "Williams", 'password': '#Password34', 'confirm_password': '#Password14'})
            assert form.validate() == False

def test_login_form_validation_passes(app, init_user_table):
    with app.app_context():
        with app.test_request_context():
            form = LoginForm(data={'login_email': 'test.user1@gmail.com', 'login_password': '#Password12345'})
            assert form.validate() == True

def test_login_form_validation_fails(app, init_user_table):
    with app.app_context():
        with app.test_request_context():
            form = LoginForm(data={'login_email': '', 'login_password': '#Password12345'})
            assert form.validate() == False