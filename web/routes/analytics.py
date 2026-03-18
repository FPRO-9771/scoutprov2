from flask import Blueprint, render_template, session

from web.auth import login_required
from web.extensions import db
from web.models.event import Event
from web.services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/')
@login_required
def dashboard():
    event_id = session['event_id']
    event = db.session.get(Event, event_id)

    unscouted_robots = AnalyticsService.get_unscouted_robots(event_id, event.game_id) if event else []
    unscouted_matches = AnalyticsService.get_unscouted_matches(event_id)
    team_averages = AnalyticsService.get_all_team_averages(event_id)
    total_teams = len(event.teams) if event else 0

    return render_template('analytics/dashboard.html',
                           unscouted_robots=unscouted_robots,
                           unscouted_matches=unscouted_matches,
                           team_averages=team_averages,
                           total_teams=total_teams)
