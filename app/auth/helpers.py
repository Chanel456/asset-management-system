import time

from flask import current_app, request

from app.models.failed_login import FailedLogin
from app.shared.shared import send_email


def check_and_alert_stuffing(ip, email):
    """Monitors recent failed login attempts anf alerts administrators when thresholds are exceeded"""
    ip_failures = FailedLogin.recent_failures_for_ip(ip)
    account_failures = FailedLogin.recent_failures_for_email(email)
    global_failures = FailedLogin.recent_global_failures()

    if ip_failures >= FailedLogin.IP_FAIL_THRESHOLD:

        send_email(
            subject='Credential Stuffing Alert',
            recipients=['security-team@yourcompany.com'],
            body=f'High number of failures from IP {ip}: {ip_failures} in 5 minutes.'
        )
        current_app.logger.warning(f'Credential stuffing suspected from IP {ip}')

    elif account_failures >= FailedLogin.ACCOUNT_FAIL_THRESHOLD:
        send_email(
            subject='Brute Force Alert',
            recipients=['security-team@yourcompany.com'],
            body=f'Account {email} had {account_failures} failed logins in 5 minutes.'
        )
        current_app.logger.warning(f'Brute force suspected on account {email}')

    elif global_failures >= FailedLogin.GLOBAL_FAIL_THRESHOLD:
        send_email(
            subject='Global Attack Alert',
            recipients=['security-team@yourcompany.com' ],
            body=f'System-wide failures: {global_failures} in 5 minutes.'
        )
        current_app.logger.warning('Global brute force/credential stuffing suspected')


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

def log_login_failure(email, reason):
    """Logs login failures and records them in failed login table"""
    FailedLogin.record_failed_login(email, request.remote_addr, request.user_agent.string)
    check_and_alert_stuffing(request.remote_addr, email)
    current_app.logger.warning(f'Login failure for email: {email}. Reason: {reason}')

