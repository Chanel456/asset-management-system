import pytest
from flask import g
from wtforms.validators import ValidationError

from app.application.form_errors import ApplicationFormError
from app.application.forms import ApplicationForm
from app.models.server import Server
from app.shared.shared import FormType


def test_application_form_passes(app, init_server_table):
    with app.app_context():
        with app.test_request_context():
            g.form_type = 'Create'
            form = ApplicationForm(data = {'name': 'Example App', 'team_name': 'Team One', 'team_email': 'teamone@gmail.com', 'url': 'https://exampleapp.com', 'swagger': 'https://exampleapp.com/swagger/ui', 'bitbucket': 'https://bitbucket.org/repos/exampleapp', 'extra_info': '', 'production_pods': 2, 'server': 'aa-1234'})
            form.server.choices = [(s.name, s.name) for s in Server.query.with_entities(Server.name)]
            assert form.validate() == True

def test_application_form_missing_required_data_validation_fails(app):
    with app.app_context():
        with app.test_request_context():
            g.form_type = 'Create'
            form = ApplicationForm(data = {'name': None, 'team_name': None , 'team_email': None , 'url': 'https://exampleapp.com', 'swagger_link': 'https://exampleapp.com/swagger/ui', 'bitbucket': 'https://bitbucket.org/repos/exampleapp', 'extra_info': '', 'production_pods': 2, 'server': 'aa-1234'})
            form.server.choices = [(s.name, s.name) for s in Server.query.with_entities(Server.name)]
            assert form.validate() == False


def test_server_form_invalid_input_validation_fails(app):
    with app.app_context():
        with app.test_request_context():
            g.form_type = 'Create'
            form = ApplicationForm(data = {'name': '1234567', 'team_name': '431689708', 'team_email': 'teamone@gmail.com', 'url': 'https://exampleappone.com', 'swagger': 'https://exampleappone.com/swagger/ui', 'bitbucket': 'https://bitbucket.org/repos/exampleappone', 'extra_info': '', 'production_pods': 2, 'server': 'aa-1234'})
            form.server.choices = [(s.name, s.name) for s in Server.query.with_entities(Server.name)]
            assert form.validate() == False
            assert form.errors.get('name')[0] == ApplicationFormError.INVALID_NAME_FORMAT.value
            assert form.errors.get('team_name')[0] == ApplicationFormError.INVALID_TEAM_NAME_FORMAT.value

def test_email_validator_passes(app):
    with app.app_context():
        with app.test_request_context():
            form = ApplicationForm()
            form.team_email.data = 'teamone@gmail.com'
            form.validate_team_email(form.team_email)
            assert len(form.team_email.errors) == 0

def test_email_validator_fails(app):
    with app.app_context():
        with app.test_request_context():
            form = ApplicationForm()
            form.team_email.data = 'teaminvalidemail@gmail'
            with pytest.raises(ValidationError):
                form.validate_team_email(form.team_email)

def test_validate_server_passes(app, init_server_table):
    with app.app_context():
        with app.test_request_context():
            form = ApplicationForm()
            form.server.data = 'aa-1234'
            form.validate_server(form.server)
            assert len(form.server.errors) == 0

def test_validate_server_fails(app, init_server_table):
    with app.app_context():
        with app.test_request_context():
            form = ApplicationForm()
            form.server.data = 'Please Select'
            with pytest.raises(ValidationError):
                form.validate_server(form.server)

def test_validate_bitbucket_passes(app):
    with app.app_context():
        with app.test_request_context():
            g.form_type = FormType.CREATE.value
            form = ApplicationForm()
            form.bitbucket.data = 'https://bitbucket.org/repo/exampleapp'
            form.validate_bitbucket(form.bitbucket)
            assert len(form.bitbucket.errors) == 0

def test_validate_bitbucket_fails(app):
    with app.app_context():
        with app.test_request_context():
            g.form_type = FormType.CREATE.value
            form = ApplicationForm()
            form.bitbucket.data = 'https://bitbucketInv$id/repos/exampleapp'
            with pytest.raises(ValidationError):
                form.validate_bitbucket(form.bitbucket)

def test_validate_swagger_passes(app):
    with app.app_context():
        with app.test_request_context():
            g.form_type = FormType.CREATE.value
            form = ApplicationForm()
            form.swagger.data = 'https://exampleapp.com/api/ui'
            form.validate_swagger(form.swagger)
            assert len(form.swagger.errors) == 0

def test_validate_swagger_fails(app):
    with app.app_context():
        with app.test_request_context():
            g.form_type = FormType.CREATE.value
            form = ApplicationForm()
            form.swagger.data = 'hts://exampleapp/swagger/'
            with pytest.raises(ValidationError):
                form.validate_swagger(form.swagger)

def test_validate_url_passes(app):
    with app.app_context():
        with app.test_request_context():
            g.form_type = FormType.CREATE.value
            form = ApplicationForm()
            form.url.data = 'https://exampleapp.com'
            form.validate_url(form.url)
            assert len(form.url.errors) == 0

def test_validate_url_fails(app):
    with app.app_context():
        with app.test_request_context():
            g.form_type = FormType.CREATE.value
            form = ApplicationForm()
            form.url.data = 'hts://exampleapp'
            with pytest.raises(ValidationError):
                form.validate_url(form.url)