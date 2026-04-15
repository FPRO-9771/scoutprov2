import json
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from web.auth import login_required
from web.extensions import db
from web.models.game import Game
from web.models.event import Event
from web.models.match import Match
from web.services.admin_service import AdminService
from web.services.import_service import ImportService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
def index():
    return render_template('admin/index.html')


# --- Games ---

@admin_bp.route('/games')
@login_required
def games():
    all_games = Game.query.all()
    return render_template('admin/games.html', games=all_games)


@admin_bp.route('/games/create', methods=['POST'])
@login_required
def create_game():
    name = request.form.get('name', '').strip()
    logo = request.form.get('logo', '').strip() or None
    if not name:
        flash('Game name is required.', 'error')
        return redirect(url_for('admin.games'))
    AdminService.create_game(name, logo=logo)
    return redirect(url_for('admin.games'))


@admin_bp.route('/games/<int:game_id>/update', methods=['POST'])
@login_required
def update_game(game_id):
    name = request.form.get('name', '').strip()
    logo = request.form.get('logo', '').strip() or None
    score_config_raw = request.form.get('score_config', '[]').strip()
    try:
        score_config = json.loads(score_config_raw)
    except json.JSONDecodeError:
        flash('Invalid JSON for score config.', 'error')
        return redirect(url_for('admin.games'))
    AdminService.update_game(game_id, name=name, logo=logo, score_config=score_config)
    return redirect(url_for('admin.games'))


# --- Events ---

@admin_bp.route('/events')
@login_required
def events():
    all_events = Event.query.order_by(Event.date.desc()).all()
    all_games = Game.query.all()
    return render_template('admin/events.html', events=all_events, games=all_games)


@admin_bp.route('/events/create', methods=['POST'])
@login_required
def create_event():
    name = request.form.get('name', '').strip()
    game_id = request.form.get('game_id', type=int)
    location = request.form.get('location', '').strip() or None
    date_str = request.form.get('date', '').strip()
    tba_event_key = request.form.get('tba_event_key', '').strip() or None

    if not name or not game_id:
        flash('Name and game are required.', 'error')
        return redirect(url_for('admin.events'))

    date = None
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    AdminService.create_event(name, game_id, location=location, date=date, tba_event_key=tba_event_key)
    return redirect(url_for('admin.events'))


@admin_bp.route('/events/<int:event_id>/update', methods=['POST'])
@login_required
def update_event(event_id):
    name = request.form.get('name', '').strip() or None
    location = request.form.get('location', '').strip() or None
    date_str = request.form.get('date', '').strip()
    tba_event_key = request.form.get('tba_event_key', '').strip() or None

    date = None
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    AdminService.update_event(event_id, name=name, location=location, date=date, tba_event_key=tba_event_key)
    return redirect(url_for('admin.events'))


# --- Teams ---

@admin_bp.route('/teams')
@login_required
def teams():
    event = db.session.get(Event, session.get('event_id'))
    team_list = sorted(event.teams, key=lambda t: t.number) if event else []
    return render_template('admin/teams.html', event=event, teams=team_list)


@admin_bp.route('/teams/add', methods=['POST'])
@login_required
def add_team():
    number = request.form.get('number', type=int)
    name = request.form.get('name', '').strip() or None
    if not number:
        flash('Team number is required.', 'error')
        return redirect(url_for('admin.teams'))

    AdminService.add_team(number, name=name)
    event_id = session.get('event_id')
    if event_id:
        AdminService.link_team_to_event(number, event_id)
    return redirect(url_for('admin.teams'))


@admin_bp.route('/teams/unlink', methods=['POST'])
@login_required
def unlink_team():
    team_number = request.form.get('team_number', type=int)
    event_id = session.get('event_id')
    if team_number and event_id:
        AdminService.unlink_team_from_event(team_number, event_id)
    return redirect(url_for('admin.teams'))


# --- Matches ---

@admin_bp.route('/matches')
@login_required
def matches():
    event = db.session.get(Event, session.get('event_id'))
    match_list = Match.query.filter_by(event_id=event.id).order_by(Match.number).all() if event else []
    return render_template('admin/matches.html', event=event, matches=match_list)


@admin_bp.route('/matches/create', methods=['POST'])
@login_required
def create_match():
    event_id = session.get('event_id')
    number = request.form.get('number', type=int)
    red_teams = [
        request.form.get('red1', type=int),
        request.form.get('red2', type=int),
        request.form.get('red3', type=int),
    ]
    blue_teams = [
        request.form.get('blue1', type=int),
        request.form.get('blue2', type=int),
        request.form.get('blue3', type=int),
    ]

    red_teams = [t for t in red_teams if t]
    blue_teams = [t for t in blue_teams if t]

    if not event_id or not number:
        flash('Event and match number are required.', 'error')
        return redirect(url_for('admin.matches'))

    AdminService.create_match(event_id, number, red_teams, blue_teams)
    return redirect(url_for('admin.matches'))


@admin_bp.route('/matches/<int:match_id>/edit', methods=['POST'])
@login_required
def edit_match(match_id):
    red_teams = [
        request.form.get('red1', type=int),
        request.form.get('red2', type=int),
        request.form.get('red3', type=int),
    ]
    blue_teams = [
        request.form.get('blue1', type=int),
        request.form.get('blue2', type=int),
        request.form.get('blue3', type=int),
    ]

    red_teams = [t for t in red_teams if t]
    blue_teams = [t for t in blue_teams if t]

    AdminService.update_match(match_id, red_teams=red_teams, blue_teams=blue_teams)
    return redirect(url_for('admin.matches'))


# --- TBA Sync ---

@admin_bp.route('/tba')
@login_required
def tba_sync():
    event = db.session.get(Event, session.get('event_id'))
    return render_template('admin/tba_sync.html', event=event)


@admin_bp.route('/tba/sync-teams', methods=['POST'])
@login_required
def sync_teams():
    event_id = session.get('event_id')
    if not event_id:
        flash('No event selected.', 'error')
        return redirect(url_for('admin.tba_sync'))

    ImportService.import_event_teams(event_id)
    return redirect(url_for('admin.tba_sync'))


@admin_bp.route('/tba/sync-matches', methods=['POST'])
@login_required
def sync_matches():
    event_id = session.get('event_id')
    if not event_id:
        flash('No event selected.', 'error')
        return redirect(url_for('admin.tba_sync'))

    ImportService.import_event_matches(event_id)
    return redirect(url_for('admin.tba_sync'))
