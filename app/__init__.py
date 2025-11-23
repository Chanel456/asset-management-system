import logging

from flask import Flask, render_template, url_for
from flask_login import LoginManager, current_user
from os import path

from werkzeug.utils import redirect

from app.extensions import db, init_extensions

DB_NAME = 'database.db'

def create_app(config_class):
    """Initialises the flask app with config, registers the blueprints and, initialises the login manager """

    app = Flask(__name__)
    app.config.from_object(config_class)
    init_extensions(app)

    logging.basicConfig(level= logging.INFO, format = f'%(asctime)s - %(levelname)s : %(message)s')

    #Import routes
    from app.views import views
    from app.auth import auth
    from app.application import application
    from app.server import server
    from app.failed_logins import failed_logins

    #Register blueprints
    app.register_blueprint(views, url_prefix='/views')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(application, url_prefix='/application')
    app.register_blueprint(server, url_prefix='/server')
    app.register_blueprint(failed_logins, url_prefix='/failed-logins')

    @app.route('/')
    def redirect_to_home():
        """Redirects base url to the dashboard html"""
        return redirect(url_for('views.dashboard'))

    @app.errorhandler(404)
    def handle_not_found_error(err):
        """Redirects to 404.html if a HTTP 404 error is thrown"""
        return render_template('error/404.html', user=current_user), 404

    @app.errorhandler(500)
    def handle_internal_server_error(err):
        """Redirects to 500.html if a 500 error is thrown"""
        return render_template('error/500.html', user=current_user), 500

    from app.models.user import User

    with app.app_context():
        if not path.exists('app/' + DB_NAME):
            db.create_all()
            logging.info('Database created')

    # Initialise login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app