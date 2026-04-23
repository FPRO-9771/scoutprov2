from flask import session

from web.extensions import db
from web.models.team import Team


def get_current_team_number():
    """Resolve the current user's team number from session. Returns None if not logged in."""
    team_id = session.get('team_id')
    if not team_id:
        return None
    team = db.session.get(Team, team_id)
    return team.number if team else None
