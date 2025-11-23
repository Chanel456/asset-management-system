from flask import render_template
from flask_login import login_required, current_user

from app.failed_logins import failed_logins
from app.models.failed_login import FailedLogin


@failed_logins.route('/all-failed-logins')
@login_required
def all_failed_logins():
    """Renders the html for the grid to view all failed logins"""
    #Checks if the current user
    if not current_user.is_admin:
        render_template('error/cannot-view-this-resource.html', user=current_user)

    failed_login = FailedLogin.fetch_all_failed_logins()
    return render_template('failed_login/grid.html', user=current_user, failed_login=failed_login)