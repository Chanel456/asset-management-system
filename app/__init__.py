import uuid

from flask import Flask, render_template, url_for, g, request, current_app, jsonify
from flask_login import LoginManager, current_user
from os import path

from werkzeug.utils import redirect

from app.extensions import db, init_extensions
from app.info import APP_NAME, APP_VERSION, DEPLOYMENT_TIME, GIT_COMMIT
from app.shared.logging import configure_logging
from config.config import Config

DB_NAME = 'database.db'

def create_app(config_class=Config):
    """Initialises the flask app with config, registers the blueprints and, initialises the login manager """

    app = Flask(__name__)
    app.config.from_object(config_class)
    init_extensions(app)

    configure_logging(app)

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
        current_app.logger.warning(
            "http:404_not_found",
            extra={
                "error": str(err),
                "error_type": type(err).__name__
            })
        return render_template('error/404.html', user=current_user), 404

    @app.errorhandler(500)
    def handle_internal_server_error(err):
        """Redirects to 500.html if a 500 error is thrown"""
        app.logger.error(f"uncaught_exception type={type(err).__name__} message={str(err)}")
        return render_template('error/500.html', user=current_user), 500

    @app.route('/info')
    def info():
        return jsonify({
            'app': APP_NAME,
            'version': APP_VERSION,
            'deployment-time': DEPLOYMENT_TIME,
            'last_commit': GIT_COMMIT
        }), 200

    @app.before_request
    def assign_request_id():
        g.request_id = str(uuid.uuid4())
        app.logger.info(f"request:start path={request.path} method={request.method}")

    @app.after_request
    def log_response(resp):
        app.logger.info(f"request:end status={resp.status_code}")
        return resp

    from app.models.user import User

    with app.app_context():
        if not path.exists('app/' + DB_NAME):
            db.create_all()
            current_app.logger.info('Database created')

    # Initialise login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app