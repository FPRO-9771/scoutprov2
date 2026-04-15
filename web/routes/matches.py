import logging
from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, abort, current_app, jsonify, render_template, session

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
        abort(404)

    event = db.session.get(Event, match.event_id)
    red_teams = _resolve_teams(match.red_teams or [])
    blue_teams = _resolve_teams(match.blue_teams or [])

    summaries = {
        team.id: TeamSummaryService.build_local(team, event)
        for team in red_teams + blue_teams
    }

    return render_template('matches/prep_detail.html',
                           match=match, red_teams=red_teams, blue_teams=blue_teams,
                           summaries=summaries)


@matches_bp.route('/prep/<int:match_id>/tba')
@login_required
def prep_tba(match_id):
    """Lazy-loaded TBA data (rank, past events, videos) for every team in the match.

    Fetches all teams in parallel so cold-cache latency is one TBA round-trip,
    not N sequential ones.
    """
    match = db.session.get(Match, match_id)
    if not match:
        abort(404)

    event = db.session.get(Event, match.event_id)
    event_key = event.tba_event_key if event else None

    team_numbers = (match.red_teams or []) + (match.blue_teams or [])
    teams = _resolve_teams(team_numbers)
    tasks = [(t.id, t.number, t.tba_key) for t in teams]

    app = current_app._get_current_object()

    def fetch(task):
        team_id, number, tba_key = task
        with app.app_context():
            return team_id, TeamSummaryService.build_tba(number, tba_key, event_key)

    results = {}
    if tasks:
        with ThreadPoolExecutor(max_workers=min(len(tasks), 8)) as pool:
            for team_id, data in pool.map(fetch, tasks):
                results[team_id] = data

    return jsonify(results)


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
