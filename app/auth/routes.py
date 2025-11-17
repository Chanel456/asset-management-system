import logging
from flask import render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user

from app.auth.forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from app.models.user import User
from app.auth import auth
from app.shared.shared import Utils

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Logs in a user to the application based on the credentials submitted in the form"""

    # redirects the user to the dashboard if they are already logged in
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))

    form = LoginForm()
    if request.method == 'POST':
        user = User.find_user_by_email(form.login_email.data)
        if user:
            if form.validate_on_submit():
                session.clear()
                login_user(user, remember = False)
                logging.info('%s logged in successfully', user.email)
                flash('Logged in successfully.', category='success')
                return redirect(url_for('views.dashboard'))
        else:
            flash('There is no account linked with this email address. Please create an account', category='error')

    return render_template('auth/login.html', user=current_user, form=form)

@auth.route('/logout')
@login_required
def logout():
    """Logout a user and redirect to the login page"""
    logging.info('User: %s successfully logged out', current_user.email)
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Registers a user and allows them to access the web application"""

    # redirects the user to the dashboard if they are already logged in
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))

    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        is_admin = True if form.account_type.data == 'admin' else False
        User.add_user(form.email.data, form.first_name.data, form.last_name.data,
                                form.password.data,is_admin)
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', user=current_user, form=form)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot():
    # redirects the user to the dashboard if they are already logged in
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))

    form = ForgotPasswordForm()
    user = User.find_user_by_email(form.email.data)

    if user:
        Utils.send_password_reset_email(user)
        flash("If that email exists, we have sent a password reset link.", category='success')

    return render_template('auth/forgot-password.html', user=current_user, form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset(token):
    #redirects the user to the dashboard if they are already logged in
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))

    form = ResetPasswordForm()
    email = Utils.verify_reset_token(token)
    if not email:
        flash('Invalid or expired token', category='error')
        return redirect(url_for('auth.forgot'))

    if request.method == 'POST' and form.validate_on_submit():
        User.update_password(email, form.password.data)
        return redirect(url_for('auth.login'))

    return render_template('auth/reset-password.html', user=current_user, form=form, token=token)