import click
from flask import current_app
from flask.cli import with_appcontext

from web.extensions import db
from web.models.game import Game
from web.models.team import Team
from web.services.import_service import ImportService


# Two target events for v1
TARGET_EVENTS = [
    '2025mitraverse',  # Traverse City, MI
    '2025mibig',       # Ferris State (Big Rapids), MI
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
