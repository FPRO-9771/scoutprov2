from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from web.auth import login_required
from web.extensions import db
from web.models.team import Team
from web.models.event import Event
from web.models.user import User
from web.services.analytics_service import AnalyticsService
from web.services.team_summary_service import TeamSummaryService

teams_bp = Blueprint('teams', __name__, url_prefix='/teams')


@teams_bp.route('/search')
@login_required
def search():
    q = request.args.get('q', '').strip()
    if not q:
        flash('Please enter a team number.', 'error')
        return redirect(url_for('main.home'))

    try:
        number = int(q)
    except ValueError:
        flash('Please enter a valid team number.', 'error')
        return redirect(url_for('main.home'))

    team = Team.query.filter_by(number=number).first()
    if not team:
        flash(f'Team {number} not found at this event.', 'error')
        return redirect(url_for('main.home'))

    event = db.session.get(Event, session['event_id'])
    if event and team not in event.teams:
        flash(f'Team {number} is not registered at {event.name}.', 'warning')
        return redirect(url_for('main.home'))

    return redirect(url_for('teams.detail', number=number))


@teams_bp.route('/<int:number>')
@login_required
def detail(number):
    team = Team.query.filter_by(number=number).first_or_404()
    event = db.session.get(Event, session['event_id'])

    summary = TeamSummaryService.build(team, event)

    outcomes = AnalyticsService.get_team_outcomes(team.id, event.id) if event else []
    user_ids = {o.user_id for o in outcomes}
    users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    scouts = {u.id: u.username for u in users}

    return render_template('teams/detail.html',
                           team=team, summary=summary,
                           outcomes=outcomes, scouts=scouts)
