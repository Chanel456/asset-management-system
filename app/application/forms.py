import validators as valid_package
from flask import g

from flask_wtf import FlaskForm
from wtforms import validators, StringField, EmailField, URLField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, ValidationError, NumberRange

from app.application.form_errors import ApplicationFormError
from app.models.application import Application
from app.shared.form_type_enum import FormType
from app.shared.general_form_error_enum import GeneralFormError


class ApplicationForm(FlaskForm):
    """
    A class to represents the input fields for adding a new application

    Fields
    --------------
    name: text
        Name of the application
    team_name: text
       Name of the development team who owns the application
    team_email : email
        Email address of development team who owns the application
    url: url
        Url for the application
    swagger: url
        Swagger link for the application if there is any
    bitbucket: url
        Url of the bitbucket repo for the application
    extra_info: text
        Any extra information other should know about the application
    production_pods: number
        The number of pods this application has up in production
    server: dropdown
        The server the application is deployed on
    """

    name = StringField('Application Name', [DataRequired(), validators.Length(min=2, max=150, message=ApplicationFormError.INVALID_NAME_LENGTH.value), validators.Regexp('^[a-zA-Z- ]+$', message=ApplicationFormError.INVALID_NAME_FORMAT.value)])
    team_name = StringField('Development team', [DataRequired(), validators.Length(min=2, max=50, message=ApplicationFormError.INVALID_TEAM_LENGTH.value), validators.Regexp('^[a-zA-Z- ]+$', message=ApplicationFormError.INVALID_TEAM_NAME_FORMAT.value)])
    team_email = EmailField('Development team email', [DataRequired(), validators.length(max=150, message=ApplicationFormError.INVALID_TEAM_EMAIL_LENGTH.value)])
    url = URLField('Application URL', [DataRequired(), validators.Length(max=150, message=ApplicationFormError.INVALID_URL_LENGTH.value)])
    swagger = URLField('Swagger URL', [validators.Optional(), validators.Length(max=200, message=ApplicationFormError.INVALID_SWAGGER_LENGTH.value)])
    bitbucket = URLField('Bitbucket URL', [DataRequired(), validators.Length(max=200, message= ApplicationFormError.INVALID_BITBUCKET_LENGTH.value)])
    extra_info = TextAreaField('Extra information', [validators.Length(max=1000, message=ApplicationFormError.INVALID_EXTRA_INFO_LENGTH.value)])
    production_pods = IntegerField('Number of production pods', [NumberRange(min=0)])
    server = SelectField('Server', [DataRequired()], coerce=str)

    def validate_name(self, field):
        """Checks if there is an application with the same name already in the Application table"""
        retrieved_application = Application.find_application_by_name(field.data)

        if ((g.form_type == FormType.UPDATE.value and retrieved_application and  retrieved_application.id != g.application_id) or
                (g.form_type == FormType.CREATE.value and retrieved_application)):
            raise ValidationError(ApplicationFormError.NAME_EXISTS.value)


    def validate_team_email(self, field):
        """Checks if the email address is valid using the validators package"""
        if not valid_package.email(field.data):
            raise ValidationError(GeneralFormError.INVALID_EMAIL.value)

    def validate_server(self, field):
        """Ensures the users has selected a server and is not submitted the placeholder field"""
        if field.data == 'Please Select':
            raise ValidationError(ApplicationFormError.SERVER_NOT_SELECTED.value)

    def validate_bitbucket(self, field):
        """Validates if bitbucket url starts with https://bitbucket.org and does not contradict to an existing one in the Application table"""

        retrieved_application = Application.find_application_by_bitbucket(field.data)

        if ((g.form_type == FormType.UPDATE.value and retrieved_application and retrieved_application.id != g.application_id) or
                (g.form_type == FormType.CREATE.value and retrieved_application)):
            raise ValidationError(ApplicationFormError.BITBUCKET_EXISTS.value)

        if not field.data.startswith('https://bitbucket.org') or not valid_package.url(field.data):
            raise ValidationError(ApplicationFormError.INVALID_BITBUCKET_FORMAT.value)

    def validate_swagger(self, field):
        """Checks if a valid url was entered for swagger and does not contradict to an existing one in the Application table"""

        retrieved_application = Application.find_application_by_swagger(field.data)

        if ((g.form_type == FormType.UPDATE.value and retrieved_application and retrieved_application.id != g.application_id) or
                (g.form_type == FormType.CREATE.value and retrieved_application)):
            raise ValidationError(ApplicationFormError.SWAGGER_EXISTS.value)

        if not valid_package.url(field.data):
            raise ValidationError(GeneralFormError.INVALID_URL.value)

    def validate_url(self, field):
        """Checks if a valid url was entered for the application url and does not contradict to an existing one in the Application table"""
        retrieved_application = Application.find_application_by_url(field.data)

        if ((g.form_type == FormType.UPDATE.value and retrieved_application and retrieved_application.id != g.application_id) or
                (g.form_type == FormType.CREATE.value and retrieved_application)):
            raise ValidationError(ApplicationFormError.URL_EXISTS.value)

        if not valid_package.url(field.data):
            raise ValidationError(GeneralFormError.INVALID_URL.value)

    def validate_production_pods(self, field):
        """Checks if a valid integer greater than or equal to 0 was entered for the production_pods field"""
        try:
            isinstance(field.data, int) and field.data >= 0
        except (TypeError, ValueError):
            raise ValidationError(GeneralFormError.INTEGER_NOT_GREATER_THAN_OR_EQUAL_TO_ZERO.value)
