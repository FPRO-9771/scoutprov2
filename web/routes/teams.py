from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from web.auth import login_required
from web.extensions import db
from web.models.team import Team
from web.models.event import Event
from web.models.robot import Robot
from web.models.user import User
from web.services.analytics_service import AnalyticsService
from web.services.tba_service import TBAService
from web.services.cache_service import CacheService

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

    # Robot build
    robot = Robot.query.filter_by(team_id=team.id, game_id=event.game_id).first() if event else None

    # Match history
    outcomes = AnalyticsService.get_team_outcomes(team.id, event.id) if event else []
    averages = AnalyticsService.get_team_match_averages(team.id, event.id) if event else None

    # Scout usernames for display
    user_ids = {o.user_id for o in outcomes}
    users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    scouts = {u.id: u.username for u in users}

    # TBA data
    rank = None
    past_events = []
    if event and event.tba_event_key:
        # Rankings
        cache_key = f'rankings:{event.tba_event_key}'
        rankings = CacheService.get(cache_key)
        if rankings is None:
            data = TBAService.get_event_rankings(event.tba_event_key)
            rankings = {}
            if data and 'rankings' in data:
                for r in data['rankings']:
                    team_num = int(r['team_key'].replace('frc', ''))
                    rankings[team_num] = r['rank']
            CacheService.set(cache_key, rankings)
        rank = rankings.get(team.number)

        # Past events
        if team.tba_key:
            pe_cache_key = f'past_events:{team.tba_key}'
            past_events = CacheService.get(pe_cache_key)
            if past_events is None:
                try:
                    year = int(event.tba_event_key[:4])
                except (ValueError, TypeError):
                    year = None
                past_events = []
                if year:
                    events_data = TBAService.get_team_events(team.tba_key, year)
                    if events_data:
                        for evt in events_data:
                            if evt.get('key') == event.tba_event_key:
                                continue
                            status = TBAService.get_team_event_status(team.tba_key, evt['key'])
                            evt_rank = None
                            if status and status.get('qual') and status['qual'].get('ranking'):
                                evt_rank = status['qual']['ranking'].get('rank')
                            past_events.append({
                                'name': evt.get('short_name') or evt.get('name', 'Unknown'),
                                'rank': evt_rank or '?',
                            })
                CacheService.set(pe_cache_key, past_events)

    return render_template('teams/detail.html',
                           team=team, robot=robot,
                           outcomes=outcomes, averages=averages, scouts=scouts,
                           rank=rank, past_events=past_events)
