import logging

from flask import Blueprint, render_template, session

from web.auth import login_required
from web.extensions import db
from web.models.event import Event
from web.models.match import Match
from web.models.team import Team
from web.models.robot import Robot
from web.services.analytics_service import AnalyticsService
from web.services.tba_service import TBAService
from web.services.cache_service import CacheService

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

    # Resolve teams
    red_teams = _resolve_teams(match.red_teams or [])
    blue_teams = _resolve_teams(match.blue_teams or [])
    all_teams = red_teams + blue_teams

    # Gather data for each team
    averages = {}
    robots = {}
    rankings = {}
    past_events = {}

    # TBA rankings (cached)
    if event and event.tba_event_key:
        rankings = _get_cached_rankings(event.tba_event_key)

    for team in all_teams:
        # Scouting averages
        summary = AnalyticsService.get_team_match_summary(team.id, event.id)
        if summary:
            averages[team.id] = summary

        # Robot build
        robot = Robot.query.filter_by(team_id=team.id, game_id=event.game_id).first() if event else None
        if robot and robot.scouting_data:
            robots[team.id] = robot.scouting_data

        # Past events (cached per team)
        if team.tba_key:
            past = _get_cached_past_events(team.tba_key, event.tba_event_key)
            if past:
                past_events[team.number] = past

    return render_template('matches/prep_detail.html',
                           match=match, red_teams=red_teams, blue_teams=blue_teams,
                           averages=averages, robots=robots,
                           rankings=rankings, past_events=past_events)


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


def _get_cached_rankings(event_key):
    cache_key = f'rankings:{event_key}'
    cached = CacheService.get(cache_key)
    if cached is not None:
        return cached

    data = TBAService.get_event_rankings(event_key)
    rankings = {}
    if data and 'rankings' in data:
        for r in data['rankings']:
            team_num = int(r['team_key'].replace('frc', ''))
            rankings[team_num] = r['rank']

    CacheService.set(cache_key, rankings)
    return rankings


def _get_cached_past_events(team_key, current_event_key):
    cache_key = f'past_events:{team_key}'
    cached = CacheService.get(cache_key)
    if cached is not None:
        return cached

    # Get year from event key (e.g., "2025mitraverse" → 2025)
    year = None
    if current_event_key:
        try:
            year = int(current_event_key[:4])
        except (ValueError, TypeError):
            pass

    if not year:
        return []

    events = TBAService.get_team_events(team_key, year)
    past = []
    if events:
        for evt in events:
            if evt.get('key') == current_event_key:
                continue
            status = TBAService.get_team_event_status(team_key, evt['key'])
            rank = None
            if status and status.get('qual') and status['qual'].get('ranking'):
                rank = status['qual']['ranking'].get('rank')
            past.append({
                'name': evt.get('short_name') or evt.get('name', 'Unknown'),
                'rank': rank or '?',
            })

    CacheService.set(cache_key, past)
    return past
