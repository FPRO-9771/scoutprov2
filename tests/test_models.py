import pytest

from web import create_app
from web.extensions import db
from web.models import Game, Event, Team, Robot, Match, Outcome, User


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'test'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session


def test_create_team(session):
    team = Team(number=9771, name='FPRO', tba_key='frc9771')
    session.add(team)
    session.commit()
    assert team.id is not None
    assert Team.query.filter_by(number=9771).first().name == 'FPRO'


def test_create_game(session):
    game = Game(name='Reefscape', score_config=[{'name': 'coral', 'max': 5}])
    session.add(game)
    session.commit()
    assert game.id is not None
    assert game.score_config[0]['name'] == 'coral'


def test_create_event_with_teams(session):
    game = Game(name='Reefscape', score_config=[])
    team = Team(number=9771, name='FPRO', tba_key='frc9771')
    session.add_all([game, team])
    session.commit()

    event = Event(game_id=game.id, name='Traverse City', tba_event_key='2026mitraverse')
    event.teams.append(team)
    session.add(event)
    session.commit()

    assert len(event.teams) == 1
    assert event.teams[0].number == 9771
    assert team.events[0].name == 'Traverse City'


def test_create_robot(session):
    team = Team(number=9771, name='FPRO')
    game = Game(name='Reefscape', score_config=[])
    session.add_all([team, game])
    session.commit()

    robot = Robot(
        team_id=team.id,
        game_id=game.id,
        scouting_data={'drive_system': 'swerve', 'ground_intake': True},
    )
    session.add(robot)
    session.commit()
    assert robot.scouting_data['drive_system'] == 'swerve'


def test_robot_unique_constraint(session):
    team = Team(number=9771, name='FPRO')
    game = Game(name='Reefscape', score_config=[])
    session.add_all([team, game])
    session.commit()

    session.add(Robot(team_id=team.id, game_id=game.id, scouting_data={}))
    session.commit()

    session.add(Robot(team_id=team.id, game_id=game.id, scouting_data={}))
    with pytest.raises(Exception):
        session.commit()


def test_create_match(session):
    game = Game(name='Reefscape', score_config=[])
    session.add(game)
    session.commit()
    event = Event(game_id=game.id, name='Traverse City')
    session.add(event)
    session.commit()

    match = Match(
        event_id=event.id,
        number=1,
        red_teams=[9771, 1234, 5678],
        blue_teams=[4321, 8765, 2468],
    )
    session.add(match)
    session.commit()
    assert match.red_teams == [9771, 1234, 5678]


def test_create_outcome(session):
    team = Team(number=9771, name='FPRO')
    game = Game(name='Reefscape', score_config=[])
    session.add_all([team, game])
    session.commit()

    user = User(team_id=team.id, username='scout1')
    event = Event(game_id=game.id, name='Traverse City')
    session.add_all([user, event])
    session.commit()

    match = Match(event_id=event.id, number=1, red_teams=[9771], blue_teams=[1234])
    session.add(match)
    session.commit()

    outcome = Outcome(
        match_id=match.id,
        team_id=team.id,
        user_id=user.id,
        scouting_data={'auton_balls': 3, 'teleop_balls': 5},
    )
    session.add(outcome)
    session.commit()
    assert outcome.created_at is not None
    assert outcome.scouting_data['auton_balls'] == 3


def test_user_unique_constraint(session):
    team = Team(number=9771, name='FPRO')
    session.add(team)
    session.commit()

    session.add(User(team_id=team.id, username='scout1'))
    session.commit()

    session.add(User(team_id=team.id, username='scout1'))
    with pytest.raises(Exception):
        session.commit()
