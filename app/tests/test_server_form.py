from flask import g

from app.server.form_errors import ServerFormError
from app.server.forms import ServerForm
from app.shared.form_type_enum import FormType


def test_form_passes(app):
    with app.app_context():
        with app.test_request_context():
            g.form_type = FormType.CREATE.value
            form = ServerForm(data = {'name': 'io-1234', 'cpu': 4567, 'memory': 23456, 'location': 'Watford'})
            assert form.validate() == True


def test_form_missing_required_data_validation_fails(app):
    with app.app_context():
        with app.test_request_context():
            g.form_type = FormType.CREATE.value
            form = ServerForm(data = {'name': 'io-1234', 'cpu': None, 'memory': 23456, 'location': None})
            assert form.validate() == False


def test_form_invalid_input_validation_fails(app):
    with app.app_context():
        with app.test_request_context():
            g.form_type = FormType.CREATE.value
            form = ServerForm(data = {'name': 'io-1234', 'cpu': 4567, 'memory': 23458, 'location': 'N0t V$L1D'})
            assert form.validate() == False
            assert form.errors.get('location')[0] == ServerFormError.INVALID_LOCATION_FORMAT.value