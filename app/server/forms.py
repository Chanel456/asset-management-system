from flask import g
from flask_wtf import FlaskForm

from wtforms import validators, StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange, ValidationError

from app.models.server import Server
from app.server.form_errors import ServerFormError
from app.shared.form_type_enum import FormType
from app.shared.general_form_error_enum import GeneralFormError


class ServerForm(FlaskForm):
    """
    A class that represents the input fields for adding a new server

    Fields
    ---------------------
    name: text
        The name of the server
    cpu: number
        The amount of CPU the server has
    memory: number
        The amount of memory the server has
    location: text
        The location of the server
    """

    name = StringField('Server Name', [DataRequired(), validators.Length(max=50, message=ServerFormError.INVALID_NAME_LENGTH.value), validators.Regexp('^[a-zA-Z0-9-]+$', message=ServerFormError.INVALID_NAME_FORMAT.value)])
    cpu = IntegerField('CPU (GHz)', [NumberRange(min=1)])
    memory = IntegerField('Memory (GiB)', [NumberRange(min=1)])
    location = StringField('Location', [DataRequired(), validators.Regexp('^[a-zA-Z\s]+$', message=ServerFormError.INVALID_LOCATION_FORMAT.value), validators.Length(max=50, message=ServerFormError.INVALID_LOCATION_LENGTH.value)])

    def validate_cpu(self, field):
        """Checks if CPU is valid"""
        check_if_valid_integer_and_greater_then_zero(field.data)


    def validate_memory(self, field):
        """Checks if Memory is valid"""
        check_if_valid_integer_and_greater_then_zero(field.data)


    def validate_name(self, field):
        """Checks if there is a server with the same name already in the Server table"""
        retrieved_server = Server.find_server_by_name(field.data)

        if ((g.form_type == FormType.UPDATE.value and retrieved_server and retrieved_server.id != g.server_id) or
                (g.form_type == FormType.CREATE.value and retrieved_server)):
            raise ValidationError(ServerFormError.NAME_EXISTS.value)


def check_if_valid_integer_and_greater_then_zero(number):
    """Checks if an integer was entered"""
    try:
        isinstance(number, int) and number >= 1
    except (TypeError, ValueError):
        raise ValidationError(GeneralFormError.INTEGER_NOT_GREATER_THAN_OR_EQUAL_TO_ONE.value)