from flask_login import current_user

from app.models.application import Application

def test_create(client, app, auth, init_server_table):
    auth.register('Test', 'Smith', 'test@gmail.com', '54321drwsP#', '54321drwsP#', 'regular')
    auth.login('test@gmail.com', '54321drwsP#')

    with client:
        with app.app_context():
            response = client.post('/application/create',
                                   data={'name': 'Example App', 'team_name': 'Team', 'team_email': 'team@gmail.com',
                                         'url': 'https://exampleapp.com', 'swagger': 'https://exampleapp.com/swagger',
                                         'bitbucket': 'https://bitbucket.org/repo/exampleapp', 'extra_info': '',
                                         'production_pods': 3, 'server': 'aa-1234'})
            assert response.status_code == 200
            application = Application.query.filter_by(name='Example App').first()
            assert application is not None


def test_update(client, app, auth, init_server_table):
    auth.register('Test', 'Smith', 'test@gmail.com', '54321drwsP#', '54321drwsP#', 'regular')
    auth.login('test@gmail.com', '54321drwsP#')

    client.post('/application/create',
                    data={'name': 'Example App', 'team_name': 'Team', 'team_email': 'team@gmail.com',
                          'url': 'https://exampleapp.com', 'swagger': 'https://exampleapp.com/swagger',
                          'bitbucket': 'https://bitbucket.org/repo/exampleapp', 'extra_info': '',
                          'production_pods': 3, 'server': 'aa-1234'})

    with app.app_context():
        application = Application.query.filter_by(name='Example App').first()
        assert application is not None
        assert application.team_email == 'team@gmail.com'

    with client:
        response = client.post(f'/application/update?application_id={application.id}',
                            data={'name': 'Example App', 'team_name': 'Team', 'team_email': 'newteamemail@gmail.com',
                                  'url': 'https://exampleapp.com', 'swagger': 'https://exampleapp.com/swagger',
                                  'bitbucket': 'https://bitbucket.org/repo/exampleapp', 'extra_info': '',
                                  'production_pods': 3, 'server': 'aa-1234'})
        assert response.status_code == 200
        application = Application.query.filter_by(id=application.id).first()
        assert application.team_email == 'newteamemail@gmail.com'



def test_delete_admin_passes(client, app, auth, init_server_table):
    auth.register('Test', 'Smith', 'test@gmail.com', '54321drwsP#', '54321drwsP#', 'admin')
    auth.login('test@gmail.com', '54321drwsP#')

    client.post('/application/create',
                data={'name': 'Example App', 'team_name': 'Team', 'team_email': 'team@gmail.com',
                          'url': 'https://exampleapp.com', 'swagger': 'https://exampleapp.com/swagger',
                          'bitbucket': 'https://bitbucket.org/repo/exampleapp', 'extra_info': '',
                          'production_pods': 3, 'server': 'aa-1234'})


    with app.app_context():
        application = Application.query.filter_by(name='Example App').first()
        assert application is not None

    with client:
        client.get(f'/application/delete?application_id={application.id}')
        application = Application.query.filter_by(name='Example App').first()
        assert application is None


def test_delete_regular_fails(client, app, auth, init_server_table):
    auth.register('Test', 'Smith', 'test@gmail.com', '54321drwsP#', '54321drwsP#', 'regular')
    auth.login('test@gmail.com', '54321drwsP#')

    client.post('/application/create',
                data={'name': 'Example App', 'team_name': 'Team', 'team_email': 'team@gmail.com',
                          'url': 'https://exampleapp.com', 'swagger': 'https://exampleapp.com/swagger',
                          'bitbucket': 'https://bitbucket.org/repo/exampleapp', 'extra_info': '',
                          'production_pods': 3, 'server': 'aa-1234'})


    with app.app_context():
        application = Application.query.filter_by(name='Example App').first()
        assert application is not None

    with client:
        client.get(f'/application/delete?application_id={application.id}')
        assert current_user.is_admin == False
        application = Application.query.filter_by(name='Example App').first()
        assert application is not None

def test_find_app_by_name_found(init_application_table):
    application = Application.find_application_by_name('App One')
    assert application is not None
    assert application.name == 'App One'
    assert application.url == 'https://appone.com'

def test_find_app_by_name_not_found(init_application_table):
    application = Application.find_application_by_name('Example App Not Found')
    assert application is None

def test_find_app_by_id_found(init_application_table):
    application = Application.find_application_by_id('13')
    assert application is not None
    assert application.name == 'App Three'
    assert application.url == 'https://appthree.com'

def test_find_app_by_id_not_found(init_application_table):
    application = Application.find_application_by_id('23456789')
    assert application is None

def test_find_app_by_url_found(init_application_table):
    application = Application.find_application_by_url('https://appone.com')
    assert application is not None
    assert application.name == 'App One'
    assert application.production_pods == 1

def test_find_app_by_url_not_found(init_application_table):
    application = Application.find_application_by_url('https://urlnotfound.com')
    assert application is None

def test_find_app_by_bitbucket_found(init_application_table):
    application = Application.find_application_by_bitbucket('https://bitbucket.org/repos/apptwo')
    assert application is not None
    assert application.name == 'App Two'
    assert application.production_pods == 1

def test_find_app_by_bitbucket_not_found(init_application_table):
    application = Application.find_application_by_bitbucket('https:/bitbucketnotfound.com')
    assert application is None