import logging

from flask import Blueprint, render_template, session

from web.auth import login_required
from web.extensions import db
from web.models.event import Event
from web.models.match import Match
from web.models.team import Team
from web.services.team_summary_service import TeamSummaryService

logger = logging.getLogger(__name__)

matches_bp = Blueprint('matches', __name__, url_prefix='/matches')

OUR_TEAM = 9771


@matches_bp.route('/prep')
@login_required
def prep_list():
    event_id = session['event_id']
    all_matches = Match.query.filter_by(event_id=event_id).order_by(Match.number).all()

    matches = []
    for match in all_matches:
        if OUR_TEAM in (match.red_teams or []):
            matches.append((match, 'red'))
        elif OUR_TEAM in (match.blue_teams or []):
            matches.append((match, 'blue'))

    return render_template('matches/prep_list.html', matches=matches)


@matches_bp.route('/prep/<int:match_id>')
@login_required
def prep_detail(match_id):
    match = db.session.get(Match, match_id)
    if not match:
        from flask import abort
        abort(404)

    event = db.session.get(Event, match.event_id)
    red_teams = _resolve_teams(match.red_teams or [])
    blue_teams = _resolve_teams(match.blue_teams or [])

    summaries = {
        team.id: TeamSummaryService.build(team, event)
        for team in red_teams + blue_teams
    }

    return render_template('matches/prep_detail.html',
                           match=match, red_teams=red_teams, blue_teams=blue_teams,
                           summaries=summaries)


@matches_bp.route('/<int:match_id>')
@login_required
def detail(match_id):
    return render_template('stub.html', title=f'Match {match_id}', message='Match detail page.')


def _resolve_teams(team_numbers):
    if not team_numbers:
        return []
    teams = Team.query.filter(Team.number.in_(team_numbers)).all()
    order = {n: i for i, n in enumerate(team_numbers)}
    teams.sort(key=lambda t: order.get(t.number, 0))
    return teams
