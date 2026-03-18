# Import all models so Alembic discovers them for migrations
from web.models.game import Game
from web.models.event import Event, event_teams
from web.models.team import Team
from web.models.robot import Robot
from web.models.match import Match
from web.models.outcome import Outcome
from web.models.user import User

__all__ = ['Game', 'Event', 'event_teams', 'Team', 'Robot', 'Match', 'Outcome', 'User']
