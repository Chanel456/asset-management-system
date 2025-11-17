from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

db = SQLAlchemy()
session_ext = Session()
mail = Mail()

def init_extensions(app):
    """
        Initialise all Flask extensions cleanly.
        Avoids circular imports and hides internal config logic.
    """
    # Initialize SQLAlchemy
    db.init_app(app)

    # Inject SQLAlchemy instance for Flask-Session *before* initializing it
    app.config["SESSION_SQLALCHEMY"] = db

    # Initialise Flask-Session
    session_ext.init_app(app)

    ## Initialise Flask-Mail
    mail.init_app(app)