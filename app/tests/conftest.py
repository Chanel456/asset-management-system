import pytest
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.application import Application
from app.models.server import Server
from app.models.user import User
from config.test_config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    app.config['WTF_CSRF_ENABLED'] = False
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def register(self, first_name, last_name, email, password, confirm_password, account_type):
        return self._client.post(
            '/auth/register',
            data={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password,
                'confirm_password': confirm_password,
                'account_type': account_type
            }
        )

    def login(self, email, password):
        return self._client.post(
           '/auth/login',
            data={
                'login_email': email,
                'login_password': password
            },
            follow_redirects = True
        )

    def logout(self):
        return  self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)

@pytest.fixture
def init_user_table(app):
    with app.app_context():
        user1 = User(first_name='Testuser1', last_name='Smith', email='test.user1@gmail.com',
                     password=generate_password_hash('54321drwsP#', method='scrypt'), is_admin=True)
        user2 = User(first_name='Testuser2', last_name='Jones', email='test.user2@gmail.com',
                     password=generate_password_hash('54321drwsP#', method='scrypt'), is_admin=True)
        user3 = User(first_name='testuser3', last_name='Davis', email='test.user3@gmail.com',
                     password=generate_password_hash('54321drwsP#', method='scrypt'), is_admin=True)
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.commit()
        yield db

@pytest.fixture
def init_application_table(app):
    with app.app_context():
        application1 = Application(name='App One', team_name='Team One',
                               team_email='team.one@gmail.com', url='https://appone.com',
                               swagger='https://appone.com/swagger/ui',
                               bitbucket='https://bitbucket.org/repos/appone', extra_info='',
                               production_pods=1, server='ab-0001')
        application2 = Application(name='App Two', team_name='Team Two',
                               team_email='team.two@gmail.com', url='https://apptwo.com',
                               swagger='',
                               bitbucket='https://bitbucket.org/repos/apptwo', extra_info='This is an angular application',
                               production_pods=1, server='ab-0002')
        application3 = Application(name='App Three', team_name='Team Three',
                               team_email='team.three@gmail.com', url='https://appthree.com',
                               swagger='https://appthree.com/swagger/ui',
                               bitbucket='https://bitbucket.org/appthree', extra_info='',
                               production_pods=1, server='ab-0003')
        db.session.add(application1)
        db.session.add(application2)
        db.session.add(application3)
        db.session.commit()
        yield db

@pytest.fixture
def init_server_table(app):
    with app.app_context():
        server1 = Server(name='aa-1234', cpu=123, memory=123, location='Walthamstow')
        server2 = Server(name='aa-2345', cpu=456, memory=456, location='Harrow')
        server3 = Server(name='aa-3456', cpu=789, memory=789, location='Surrey')
        db.session.add(server1)
        db.session.add(server2)
        db.session.add(server3)
        db.session.commit()
        yield db