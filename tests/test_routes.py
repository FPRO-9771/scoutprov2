import pytest

from web import create_app
from web.extensions import db
from web.models import Team, User, Event, Game


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'test'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        # Seed team 9771
        team = Team(number=9771, name='FPRO', tba_key='frc9771')
        db.session.add(team)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_redirects_to_home(client):
    resp = client.get('/')
    assert resp.status_code == 302
    assert '/home' in resp.headers['Location']


def test_home_redirects_to_login(client):
    resp = client.get('/home')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_login_page_renders(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b'ScoutPro' in resp.data


def test_create_user(client):
    resp = client.post('/login', data={'username': 'testscout'}, follow_redirects=False)
    assert resp.status_code == 302
    assert '/events' in resp.headers['Location']


def test_create_duplicate_user(client, app):
    with app.app_context():
        team = Team.query.filter_by(number=9771).first()
        db.session.add(User(team_id=team.id, username='scout1'))
        db.session.commit()

    client.post('/login', data={'username': 'scout1'})
    resp = client.get('/login')
    assert resp.status_code == 200


def test_select_existing_user(client, app):
    with app.app_context():
        team = Team.query.filter_by(number=9771).first()
        user = User(team_id=team.id, username='scout1')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    resp = client.get(f'/login?select_user={user_id}', follow_redirects=False)
    assert resp.status_code == 302
    assert '/events' in resp.headers['Location']


def test_logout_clears_session(client):
    client.post('/login', data={'username': 'testscout'})
    resp = client.get('/logout', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']

    resp = client.get('/home')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_event_selection(client, app):
    # Create user first
    client.post('/login', data={'username': 'testscout'})

    with app.app_context():
        game = Game(name='Reefscape', score_config=[])
        db.session.add(game)
        db.session.commit()
        event = Event(game_id=game.id, name='Traverse City', location='TC, MI')
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    resp = client.get(f'/events?event_id={event_id}', follow_redirects=False)
    assert resp.status_code == 302
    assert '/' == resp.headers['Location'] or resp.headers['Location'].endswith('/')


def test_events_page_renders(client):
    client.post('/login', data={'username': 'testscout'})
    resp = client.get('/events')
    assert resp.status_code == 200
    assert b'Select Event' in resp.data
