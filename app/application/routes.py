from flask import render_template, request, flash, redirect, url_for, g
from flask_login import login_required, current_user

from app.application import application
from app.application.forms import ApplicationForm
from app.application.form_errors import ApplicationFormError
from app.models.application import Application
from app.models.server import Server
from app.shared.form_type_enum import FormType


@application.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Creates an application in the database using the information entered by the form"""

    form = ApplicationForm()
    g.form_type = FormType.CREATE.value

    # Populating server dropdown with values from the server table
    servers = Server.fetch_server_with_entity(Server.name)
    form.server.choices = [(s.name, s.name) for s in servers]
    form.server.choices.insert(0, ('Please Select', 'Please Select'))

    if request.method == 'POST' and form.validate_on_submit():
        #If the form is valid add application to database
        Application.create_application(form.name.data, form.team_name.data, form.team_email.data, form.url.data,
                                        form.swagger.data, form.bitbucket.data, form.production_pods.data,
                                        form.extra_info.data, form.server.data)

    return render_template('application/add-application.html', user=current_user, form=form, application_form_error = ApplicationFormError)

@application.route('/update', methods=['POST', 'GET'])
@login_required
def update():
    """Updates an applications details in the database. This endpoint takes a query parameter of the applications id"""

    application_id = request.args.get('application_id')

    # Assigning global variables to be used in custom form validation functions
    g.form_type = FormType.UPDATE.value
    g.application_id = int(application_id)

    retrieved_application = Application.find_application_by_id(application_id)
    form = ApplicationForm(obj = retrieved_application)
    form.server.choices = [(s.name, s.name) for s in Server.query.with_entities(Server.name)]

    if request.method == 'POST' and form.validate_on_submit():
        updated_application = form.data
        updated_application.pop('csrf_token', None)
        if retrieved_application:
            Application.update_application(application_id, updated_application)
        else:
            message = f'Application {retrieved_application.name} cannot be updated as they do not exist'
            flash(message, category='error',)

    return render_template('application/update-application.html', user = current_user, application = retrieved_application, form = form, application_form_error = ApplicationFormError)

@application.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    """This function deletes and application from the database. This action can only be completed my admin user.
    This function takes a query parameter of the application id"""

    # Checks GET request was made to the endpoint and is user is an admin
    if request.method == 'GET' and current_user.is_admin:
        application_id = request.args.get('application_id')
        retrieved_application = Application.find_application_by_id(application_id)

        #Deletes server
        if retrieved_application:
            Application.delete_application(retrieved_application)
        else:
            message = f'Application {retrieved_application} cannot be deleted as it does not exist'
            flash(message, category='error')

    return redirect(url_for('application.all_applications'))

@application.route('/all-applications')
@login_required
def all_applications():
    """Renders the html for the grid to view all applications"""
    applications = Application.fetch_all_applications()
    return render_template('application/grid.html', user=current_user, applications=applications)