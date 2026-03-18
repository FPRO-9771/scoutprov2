import pytest

from web.extensions import db
from web.models import Game, Team, Event, Match, Robot, Outcome, User
from web.services.robot_service import RobotService
from web.services.outcome_service import OutcomeService
from web.services.analytics_service import AnalyticsService
from web.services.admin_service import AdminService


@pytest.fixture
def ctx(app):
    with app.app_context():
        team = Team(number=9771, name='FPRO')
        game = Game(name='Reefscape', score_config=[])
        db.session.add_all([team, game])
        db.session.commit()

        event = Event(game_id=game.id, name='Test Event')
        event.teams.append(team)
        db.session.add(event)
        db.session.commit()

        user = User(team_id=team.id, username='scout1')
        db.session.add(user)
        db.session.commit()

        match = Match(event_id=event.id, number=1, red_teams=[9771], blue_teams=[1234])
        db.session.add(match)
        db.session.commit()

        yield {
            'team': team, 'game': game, 'event': event,
            'user': user, 'match': match,
        }


# --- Robot Service ---

def test_save_and_get_robot(ctx):
    data = {'drive_system': 'swerve', 'ground_intake': True}
    robot = RobotService.save_robot(ctx['team'].id, ctx['game'].id, data)
    assert robot.scouting_data['drive_system'] == 'swerve'

    fetched = RobotService.get_robot(ctx['team'].id, ctx['game'].id)
    assert fetched.id == robot.id


def test_save_robot_upsert(ctx):
    RobotService.save_robot(ctx['team'].id, ctx['game'].id, {'drive_system': 'tank'})
    RobotService.save_robot(ctx['team'].id, ctx['game'].id, {'drive_system': 'swerve'})
    robot = RobotService.get_robot(ctx['team'].id, ctx['game'].id)
    assert robot.scouting_data['drive_system'] == 'swerve'
    assert Robot.query.count() == 1


def test_scouted_status(ctx):
    status = RobotService.get_scouted_status(ctx['event'].id, ctx['game'].id)
    assert status[ctx['team'].id] is False

    RobotService.save_robot(ctx['team'].id, ctx['game'].id, {'drive_system': 'swerve'})
    status = RobotService.get_scouted_status(ctx['event'].id, ctx['game'].id)
    assert status[ctx['team'].id] is True


# --- Outcome Service ---

def test_save_and_get_outcome(ctx):
    data = {'auton_balls': 3, 'teleop_balls': 4}
    outcome = OutcomeService.save_outcome(ctx['match'].id, ctx['team'].id, ctx['user'].id, data)
    assert outcome.scouting_data['auton_balls'] == 3

    fetched = OutcomeService.get_outcome(ctx['match'].id, ctx['team'].id, ctx['user'].id)
    assert fetched.id == outcome.id


def test_save_outcome_upsert(ctx):
    OutcomeService.save_outcome(ctx['match'].id, ctx['team'].id, ctx['user'].id, {'auton_balls': 1})
    OutcomeService.save_outcome(ctx['match'].id, ctx['team'].id, ctx['user'].id, {'auton_balls': 5})
    outcome = OutcomeService.get_outcome(ctx['match'].id, ctx['team'].id, ctx['user'].id)
    assert outcome.scouting_data['auton_balls'] == 5
    assert Outcome.query.count() == 1


def test_match_scout_counts(ctx):
    OutcomeService.save_outcome(ctx['match'].id, ctx['team'].id, ctx['user'].id, {'auton_balls': 3})
    counts = OutcomeService.get_match_scout_counts(ctx['match'].id)
    assert counts[ctx['team'].id] == 1


def test_event_match_scout_status(ctx):
    status = OutcomeService.get_event_match_scout_status(ctx['event'].id)
    assert status[ctx['match'].id] == 'none'

    OutcomeService.save_outcome(ctx['match'].id, ctx['team'].id, ctx['user'].id, {'auton_balls': 3})
    status = OutcomeService.get_event_match_scout_status(ctx['event'].id)
    assert status[ctx['match'].id] == 'partial'


# --- Analytics Service ---

def test_team_match_averages(ctx):
    assert AnalyticsService.get_team_match_averages(ctx['team'].id, ctx['event'].id) is None

    OutcomeService.save_outcome(ctx['match'].id, ctx['team'].id, ctx['user'].id,
                                {'auton_balls': 2, 'teleop_balls': 4})
    avgs = AnalyticsService.get_team_match_averages(ctx['team'].id, ctx['event'].id)
    assert avgs['auton_balls'] == 2.0
    assert avgs['teleop_balls'] == 4.0


def test_team_match_summary(ctx):
    OutcomeService.save_outcome(ctx['match'].id, ctx['team'].id, ctx['user'].id,
                                {'auton_balls': 3, 'teleop_climb': 2})
    summary = AnalyticsService.get_team_match_summary(ctx['team'].id, ctx['event'].id)
    assert summary['count'] == 1
    assert summary['auton_balls']['avg'] == 3.0
    assert summary['teleop_climb']['min'] == 2


def test_get_unscouted_robots(ctx):
    unscouted = AnalyticsService.get_unscouted_robots(ctx['event'].id, ctx['game'].id)
    assert len(unscouted) == 1
    assert unscouted[0].number == 9771

    RobotService.save_robot(ctx['team'].id, ctx['game'].id, {'drive_system': 'swerve'})
    unscouted = AnalyticsService.get_unscouted_robots(ctx['event'].id, ctx['game'].id)
    assert len(unscouted) == 0


def test_get_all_team_averages(ctx):
    results = AnalyticsService.get_all_team_averages(ctx['event'].id)
    assert len(results) == 1
    assert results[0]['team'].number == 9771
    assert results[0]['match_count'] == 0


# --- Admin Service ---

def test_create_match(ctx):
    match = AdminService.create_match(ctx['event'].id, 99, [9771], [1234])
    assert match.number == 99
    assert match.red_teams == [9771]


def test_update_match(ctx):
    AdminService.update_match(ctx['match'].id, red_teams=[1111, 2222, 3333])
    match = db.session.get(Match, ctx['match'].id)
    assert match.red_teams == [1111, 2222, 3333]


def test_add_team(ctx):
    team = AdminService.add_team(9999, name='NewBot')
    assert team.number == 9999
    # Adding again returns existing
    same = AdminService.add_team(9999)
    assert same.id == team.id
