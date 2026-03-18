import pytest

from web import create_app
from web.extensions import db as _db
from web.models import Game, Team, Event, Match, User


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'test'
    TBA_API_KEY = 'test-key'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded_app(app):
    """App with team 9771, a game, event, teams, matches, and a user."""
    with app.app_context():
        team = Team(number=9771, name='FPRO', tba_key='frc9771')
        team2 = Team(number=1234, name='TestBot', tba_key='frc1234')
        team3 = Team(number=5678, name='RoboTeam', tba_key='frc5678')
        game = Game(name='Reefscape', score_config=[])
        _db.session.add_all([team, team2, team3, game])
        _db.session.commit()

        event = Event(game_id=game.id, name='Traverse City', tba_event_key='2025mitraverse')
        event.teams.extend([team, team2, team3])
        _db.session.add(event)
        _db.session.commit()

        match = Match(event_id=event.id, number=1,
                      red_teams=[9771, 1234, 5678], blue_teams=[4321, 8765, 2468])
        _db.session.add(match)
        _db.session.commit()

        user = User(team_id=team.id, username='testscout')
        _db.session.add(user)
        _db.session.commit()

    yield app


@pytest.fixture
def authed_client(seeded_app):
    """Client logged in with a user and event selected."""
    client = seeded_app.test_client()
    with client.session_transaction() as sess:
        with seeded_app.app_context():
            user = User.query.filter_by(username='testscout').first()
            event = Event.query.first()
            sess['user_id'] = user.id
            sess['username'] = user.username
            sess['team_id'] = user.team_id
            sess['event_id'] = event.id
            sess['event_name'] = event.name
    return client
