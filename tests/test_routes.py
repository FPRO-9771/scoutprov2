import pytest

from web.extensions import db
from web.models import Team, User, Event, Game


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


def test_create_user(client, app):
    with app.app_context():
        Team(number=9771, name='FPRO', tba_key='frc9771')
        db.session.add(Team(number=9771, name='FPRO', tba_key='frc9771'))
        db.session.commit()

    resp = client.post('/login', data={'username': 'testscout'}, follow_redirects=False)
    assert resp.status_code == 302
    assert '/events' in resp.headers['Location']


def test_create_duplicate_user(client, app):
    with app.app_context():
        team = Team(number=9771, name='FPRO', tba_key='frc9771')
        db.session.add(team)
        db.session.commit()
        db.session.add(User(team_id=team.id, username='scout1'))
        db.session.commit()

    client.post('/login', data={'username': 'scout1'})
    resp = client.get('/login')
    assert resp.status_code == 200


def test_select_existing_user(client, app):
    with app.app_context():
        team = Team(number=9771, name='FPRO', tba_key='frc9771')
        db.session.add(team)
        db.session.commit()
        user = User(team_id=team.id, username='scout1')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    resp = client.get(f'/login?select_user={user_id}', follow_redirects=False)
    assert resp.status_code == 302
    assert '/events' in resp.headers['Location']


def test_logout_clears_session(client, app):
    with app.app_context():
        db.session.add(Team(number=9771, name='FPRO', tba_key='frc9771'))
        db.session.commit()

    client.post('/login', data={'username': 'testscout'})
    resp = client.get('/logout', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']

    resp = client.get('/home')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_event_selection(client, app):
    with app.app_context():
        db.session.add(Team(number=9771, name='FPRO', tba_key='frc9771'))
        db.session.commit()

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


def test_events_page_renders(client, app):
    with app.app_context():
        db.session.add(Team(number=9771, name='FPRO', tba_key='frc9771'))
        db.session.commit()

    client.post('/login', data={'username': 'testscout'})
    resp = client.get('/events')
    assert resp.status_code == 200
    assert b'Select Event' in resp.data


def test_home_renders_with_session(authed_client):
    resp = authed_client.get('/home')
    assert resp.status_code == 200
    assert b'Match Prep' in resp.data


def test_robot_list_renders(authed_client):
    resp = authed_client.get('/scout/robots')
    assert resp.status_code == 200
    assert b'Scout a Robot' in resp.data


def test_match_list_renders(authed_client):
    resp = authed_client.get('/scout/matches')
    assert resp.status_code == 200
    assert b'Scout a Match' in resp.data


def test_analytics_renders(authed_client):
    resp = authed_client.get('/analytics/')
    assert resp.status_code == 200
    assert b'Analytics' in resp.data


def test_admin_renders(authed_client):
    resp = authed_client.get('/admin/')
    assert resp.status_code == 200
    assert b'Admin Panel' in resp.data


def test_404_page(authed_client):
    resp = authed_client.get('/nonexistent-page')
    assert resp.status_code == 404
    assert b'Page not found' in resp.data


def test_team_search_redirects(authed_client):
    resp = authed_client.get('/teams/search?q=9771', follow_redirects=False)
    assert resp.status_code == 302
    assert '/teams/9771' in resp.headers['Location']


def test_team_search_not_found(authed_client):
    resp = authed_client.get('/teams/search?q=9999', follow_redirects=True)
    assert b'not found' in resp.data or b'not registered' in resp.data
