import logging
import time

from flask import current_app, redirect, url_for, flash, request
from itsdangerous import URLSafeTimedSerializer

from app.models.failed_login import FailedLogin
from app.models.user import User
from app.shared.shared import send_email


def generate_reset_token(user):
    """Generates a reset token """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    logging.info(user.password)
    return serializer.dumps(
        {'email': user.email, 'pw_hash': user.password},
        salt='password-reset'
    )

def verify_reset_token(token, expiration=3600):
    """Verifies the token has not expired when the user tries to reset their email"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token, salt='password-reset', max_age=3600)
    except Exception as err:
        logging.error(f'Invalid or expired reset token: {err}')
        return redirect(url_for('auth.forgot'))

    email = data.get("email")
    pw_hash = data.get("pw_hash")

    user = User.find_user_by_email(email)
    if not user:
        logging.error('Reset token refers to unknown user.')
        return redirect(url_for('auth.forgot'))

    # Invalidate token automatically if password was changed
    if pw_hash != user.password:
        flash('Reset token invalidated because password has changed.', category='error')
        return redirect(url_for('auth.forgot'))

    return email

def send_password_reset_email(user):
    """
    Sends the password reset email to a user.
    """
    token = generate_reset_token(user)

    reset_url = url_for("auth.reset", token=token, _external=True)
    logging.info(reset_url)

    subject = 'Password Reset Request'
    body = f'To reset your password, click the following link:\n{reset_url}'
    html = f"<p>To reset your password, click the following link:</p><p><a href='{reset_url}'>{reset_url}</a></p>"

    send_email(subject, [user.email], body, html)

def check_and_alert_stuffing(ip, email):
    """Monitors recent failed login attempts anf alerts administrators when thresholds are exceeded"""
    ip_failures = FailedLogin.recent_failures_for_ip(ip)
    account_failures = FailedLogin.recent_failures_for_email(email)
    global_failures = FailedLogin.recent_global_failures()

    if ip_failures >= FailedLogin.IP_FAIL_THRESHOLD:

        send_email(
            subject="Credential Stuffing Alert",
            recipients=["security-team@yourcompany.com"],
            body=f"High number of failures from IP {ip}: {ip_failures} in 5 minutes."
        )
        logging.warning(f"Credential stuffing suspected from IP {ip}")

    elif account_failures >= FailedLogin.ACCOUNT_FAIL_THRESHOLD:
        send_email(
            subject="Brute Force Alert",
            recipients=["security-team@yourcompany.com"],
            body=f"Account {email} had {account_failures} failed logins in 5 minutes."
        )
        logging.warning(f"Brute force suspected on account {email}")

    elif global_failures >= FailedLogin.GLOBAL_FAIL_THRESHOLD:
        send_email(
            subject="Global Attack Alert",
            recipients=["security-team@yourcompany.com"],
            body=f"System-wide failures: {global_failures} in 5 minutes."
        )
        logging.warning("Global brute force/credential stuffing suspected")

def apply_adaptive_friction(user, email, ip):
    """Delays logins after unsuccessful attempts"""

    # Base exponential backoff
    base_delay = min(2 ** user.failed_attempts, 8)

    # Add extra delay if suspicious
    if FailedLogin.recent_failures_for_ip(ip) >= FailedLogin.IP_FAIL_THRESHOLD:
        base_delay += 5
    if FailedLogin.recent_failures_for_email(email) >= FailedLogin.ACCOUNT_FAIL_THRESHOLD:
        base_delay += 5
    if FailedLogin.recent_global_failures() >= FailedLogin.GLOBAL_FAIL_THRESHOLD:
        base_delay += 10

    time.sleep(base_delay)

def log_failure(email, reason):
    """Logs login failures and records them in failed login table"""
    FailedLogin.record_failed_login(email, request.remote_addr, request.user_agent.string)
    check_and_alert_stuffing(request.remote_addr, email)
    logging.warning(
        f'Login failure | email={email} | ip={request.remote_addr} '
        f'| user_agent={request.user_agent.string} | reason={reason}'
    )
