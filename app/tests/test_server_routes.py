from flask_login import current_user

from app.models.server import Server

def test_create(client, app, auth):
    auth.register('Test', 'Smith', 'test@gmail.com', '54321drwsP#', '54321drwsP#', 'regular')
    auth.login('test@gmail.com', '54321drwsP#')

    with client:
        with app.app_context():
            response = client.post('/server/create',
                                        data={'name': 'io-9877', 'cpu': 123, 'memory': 123, 'location': 'Nottingham'})
            assert response.status_code == 200
            server = Server.query.filter_by(name='io-9877').first()
            assert server is not None


def test_update(client, app, auth):
    auth.register('Test', 'Smith', 'test@gmail.com', '54321drwsP#', '54321drwsP#', 'regular')
    auth.login('test@gmail.com', '54321drwsP#')

    client.post('/server/create',
                data={'name': 'io-9877', 'cpu': 123, 'memory': 123, 'location': 'Nottingham'})

    with app.app_context():
        server = Server.query.filter_by(name='io-9877').first()
        assert server is not None

    with client:
        response = client.post(f'server/update?server_id={server.id}',
                               data={'name': 'io-9877', 'cpu': 967, 'memory': 123, 'location': 'Nottingham'})
        assert response.status_code == 200
        server = Server.query.filter_by(name='io-9877').first()
        assert server.cpu == 967



def test_delete_admin_passes(client, app, auth):
    auth.register('Test', 'Smith', 'test@gmail.com', '54321drwsP#', '54321drwsP#', 'admin')
    auth.login('test@gmail.com', '54321drwsP#')

    client.post('/server/create',
                data={'name': 'io-9877', 'cpu': 123, 'memory': 123, 'location': 'Nottingham'})


    with app.app_context():
        server = Server.query.filter_by(name='io-9877').first()
        assert server is not None

    with client:
        client.get(f'/server/delete?server_id={server.id}' )
        server = Server.query.filter_by(name='io-9877').first()
        assert server is None


def test_delete_regular_fails(client, app, auth):
    auth.register('Test', 'Smith', 'test@gmail.com', '54321drwsP#', '54321drwsP#', 'regular')
    auth.login('test@gmail.com', '54321drwsP#')

    client.post('/server/create',
                data={'name': 'io-9877', 'cpu': 123, 'memory': 123, 'location': 'Nottingham'})


    with app.app_context():
        server = Server.query.filter_by(name='io-9877').first()
        assert server is not None

    with client:
        client.get(f'/server/delete?server_id={server.id}')
        assert current_user.is_admin == False
        server = Server.query.filter_by(name='io-9877').first()
        assert server is not None