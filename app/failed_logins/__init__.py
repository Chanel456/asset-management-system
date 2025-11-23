from flask import Blueprint

failed_logins = Blueprint('failed_logins', __name__)

from app.failed_logins import routes

