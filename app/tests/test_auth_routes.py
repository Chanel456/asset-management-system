from flask import session
from flask_login import current_user

from app.models.user import User


def test_registration(app, auth):
    auth.register('Test', 'Smith', 'test@gmail.com', '54321drwsP#', '54321drwsP#', 'regular')
    with app.app_context():
        assert User.query.first().email == 'test@gmail.com'

def test_login(client, auth):
    auth.register('Test', 'Smith','test@gmail.com', '54321drwsP#', '54321drwsP#', 'regular')
    response = auth.login('test@gmail.com', '54321drwsP#')
    assert response.status_code == 200

    with client:
        client.get('/views/dashboard')
        assert session['_user_id'] == '1'
        assert current_user.email == 'test@gmail.com'


def test_logout(auth):
    auth.register('Test', 'Smith', 'test@gmail.com', '54321drwsP#', '54321drwsP#', 'regular')
    auth.login('test@gmail.com', '54321drwsP#')
    response = auth.logout()
    assert response.headers['Location'] == '/auth/login'