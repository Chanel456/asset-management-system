from flask import render_template, flash, request, url_for, redirect, g
from flask_login import login_required, current_user

from app.models.server import Server
from app.server import server
from app.server.form_errors import ServerFormError
from app.server.forms import ServerForm
from app.shared.form_type_enum import FormType


@server.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Creates a server in the database using the information entered by the form"""
    form = ServerForm()

    # Assigning global variables to be used in custom form validation functions
    g.form_type = FormType.CREATE.value

    # If the create form is valid add server to database
    if request.method == 'POST' and form.validate_on_submit():
            Server.create_server(form.name.data, form.cpu.data, form.memory.data, form.location.data)

    return render_template('server/add-server.html', user=current_user, form=form, server_form_error= ServerFormError)

@server.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    """Updates a servers details in the database. This endpoint takes a query parameter of the server id"""

    server_id = request.args.get('server_id')
    retrieved_server = Server.find_server_by_id(server_id)
    form = ServerForm(obj=retrieved_server)

    # Assigning global variables to be used in custom form validation functions
    g.form_type = FormType.UPDATE.value
    g.server_id = int(server_id)

    # If form is valid update server information
    if request.method == 'POST' and  form.validate_on_submit():
        updated_server = form.data
        # Remove csrf_token form object
        updated_server.pop('csrf_token', None)
        if retrieved_server:
            Server.update_server(server_id, updated_server)
        else:
            message = f'Server {retrieved_server.name} cannot be updated as they do not exist'
            flash(message, category='error', )

    return render_template('server/update-server.html', user=current_user, form=form, server = retrieved_server, server_form_error= ServerFormError)


@server.route('/delete', methods=['GET'])
@login_required
def delete():
    """This function deletes and server from the database. This action can only be completed my admin user.
        This function takes a query parameter of the server id"""

    # Checks GET request was made to the endpoint and is user is an admin
    if request.method == 'GET' and current_user.is_admin:
        server_id = request.args.get('server_id')
        retrieved_server = Server.find_server_by_id(server_id)
        applications_deployed_on_server = retrieved_server.applications

        # Checks if there are applications deployed on the server proposed to be deleted
        if applications_deployed_on_server:
            applications = ', '.join([app.name for app in applications_deployed_on_server])
            message = f'Server {retrieved_server.name} cannot be deleted as application(s) {applications} are running on it'
            flash(message, category='error')
        # Delete server
        elif retrieved_server:
            Server.delete_server(retrieved_server)
        else:
            message = f'Server {retrieved_server.name} cannot be deleted as it does not exist'
            flash(message, category='error')

    return redirect(url_for('server.all_servers'))

@server.route('/all-servers')
@login_required
def all_servers():
    """Renders the html for the grid to view all servers"""
    servers = Server.fetch_all_servers()
    return render_template('server/grid.html', user=current_user, list=servers)