import random

import click
from flask import current_app
from flask.cli import with_appcontext

from web.extensions import db
from web.models.game import Game
from web.models.team import Team
from web.models.user import User
from web.models.event import Event
from web.models.match import Match
from web.models.robot import Robot
from web.models.outcome import Outcome
from web.services.import_service import ImportService


# Two target events for v1
TARGET_EVENTS = [
    '2026mitvc',   # Traverse City, MI
    '2026mibig',   # Ferris State (Big Rapids), MI
]


@click.command('seed')
@with_appcontext
def seed_command():
    """Seed team 9771, Rebuilt game, and import target events + teams."""
    # Team 9771
    team = Team.query.filter_by(number=9771).first()
    if not team:
        team = Team(number=9771, name='FPRO', tba_key='frc9771')
        db.session.add(team)
        db.session.commit()
        click.echo('Created team 9771 FPRO')
    else:
        click.echo('Team 9771 already exists')

    # Game
    game = Game.query.filter_by(name='Reefscape').first()
    if not game:
        game = Game(name='Reefscape', score_config=[])
        db.session.add(game)
        db.session.commit()
        click.echo('Created game: Reefscape')
    else:
        click.echo('Game Reefscape already exists')

    # Import events
    if not current_app.config.get('TBA_API_KEY'):
        click.echo('TBA_API_KEY not set — skipping event import. Set it in .env to import events.')
        return

    for event_key in TARGET_EVENTS:
        event = ImportService.import_event(event_key, game.id)
        if event:
            count = ImportService.import_event_teams(event.id)
            click.echo(f'Imported event {event.name} with {count} teams')
        else:
            click.echo(f'Could not import event {event_key}')


@click.command('import-matches')
@click.argument('event_key')
@with_appcontext
def import_matches_command(event_key):
    """Pull match schedule from TBA for an event."""
    from web.models.event import Event

    event = Event.query.filter_by(tba_event_key=event_key).first()
    if not event:
        click.echo(f'Event {event_key} not found in DB. Run `flask seed` first.')
        return

    count = ImportService.import_event_matches(event.id)
    click.echo(f'Imported {count} matches for {event.name}')


@click.command('seed-demo')
@with_appcontext
def seed_demo_command():
    """Seed demo scouting data for testing analytics and UI."""
    # Ensure base seed exists
    game = Game.query.first()
    if not game:
        click.echo('Run `flask seed` first.')
        return

    event = Event.query.first()
    if not event:
        click.echo('No events found. Run `flask seed` first.')
        return

    # Create a test user
    user = User.query.filter_by(username='demo-scout').first()
    if not user:
        team = Team.query.filter_by(number=9771).first()
        if not team:
            click.echo('Team 9771 not found. Run `flask seed` first.')
            return
        user = User(team_id=team.id, username='demo-scout')
        db.session.add(user)
        db.session.commit()
        click.echo('Created demo user: demo-scout')

    # Create sample matches if none exist
    if Match.query.filter_by(event_id=event.id).count() == 0:
        teams = [t.number for t in event.teams]
        if len(teams) < 6:
            click.echo('Need at least 6 teams. Import more teams first.')
            return
        for i in range(1, 11):
            random.shuffle(teams)
            match = Match(
                event_id=event.id, number=i,
                red_teams=teams[:3], blue_teams=teams[3:6],
            )
            db.session.add(match)
        db.session.commit()
        click.echo('Created 10 demo matches')

    # Seed robot builds
    drive_systems = ['tank', 'swerve']
    shooter_systems = ['fixed', 'turret']
    climbs = ['none', 'L1', 'L2', 'L3']
    robot_count = 0
    for team in event.teams:
        existing = Robot.query.filter_by(team_id=team.id, game_id=game.id).first()
        if not existing:
            robot = Robot(
                team_id=team.id, game_id=game.id,
                scouting_data={
                    'drive_system': random.choice(drive_systems),
                    'ground_intake': random.choice([True, False]),
                    'shooter_system': random.choice(shooter_systems),
                    'climb': random.choice(climbs),
                },
            )
            db.session.add(robot)
            robot_count += 1
    db.session.commit()
    click.echo(f'Seeded {robot_count} robot builds')

    # Seed match outcomes
    matches = Match.query.filter_by(event_id=event.id).all()
    outcome_count = 0
    for match in matches:
        all_numbers = (match.red_teams or []) + (match.blue_teams or [])
        for num in all_numbers:
            team = Team.query.filter_by(number=num).first()
            if not team:
                continue
            existing = Outcome.query.filter_by(
                match_id=match.id, team_id=team.id, user_id=user.id
            ).first()
            if not existing:
                outcome = Outcome(
                    match_id=match.id, team_id=team.id, user_id=user.id,
                    scouting_data={
                        'auton_balls': random.randint(0, 5),
                        'auton_climb': random.randint(0, 3),
                        'teleop_balls': random.randint(0, 5),
                        'teleop_defense': random.randint(0, 3),
                        'teleop_climb': random.randint(0, 3),
                    },
                )
                db.session.add(outcome)
                outcome_count += 1
    db.session.commit()
    click.echo(f'Seeded {outcome_count} match outcomes')
    click.echo('Demo data seeding complete!')
