from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort

from web.auth import login_required
from web.extensions import db
from web.models.event import Event
from web.models.match import Match
from web.models.team import Team
from web.services.outcome_service import OutcomeService
from web.services.robot_service import RobotService

scouting_bp = Blueprint('scouting', __name__, url_prefix='/scout')


# --- Robot Scouting ---

@scouting_bp.route('/robots')
@login_required
def robot_list():
    event = db.session.get(Event, session['event_id'])
    scouted = RobotService.get_scouted_status(session['event_id'], event.game_id) if event else {}
    sort = request.args.get('sort', 'number')
    if event:
        if sort == 'status':
            teams = sorted(event.teams, key=lambda t: (bool(scouted.get(t.id)), t.number))
        else:
            teams = sorted(event.teams, key=lambda t: t.number)
    else:
        teams = []
    return render_template('scouting/robot_list.html', teams=teams, scouted=scouted, sort=sort)


@scouting_bp.route('/robot/<int:team_number>')
@login_required
def robot_input(team_number):
    team = Team.query.filter_by(number=team_number).first_or_404()
    event = db.session.get(Event, session['event_id'])
    robot = RobotService.get_robot(team.id, event.game_id) if event else None
    data = robot.scouting_data if robot else {}
    if 'ground_intake' in data:
        if isinstance(data['ground_intake'], bool):
            data['ground_intake'] = 'yes' if data['ground_intake'] else 'no'
    return render_template('scouting/robot_input.html', team=team, data=data)


@scouting_bp.route('/robot/<int:team_number>', methods=['POST'])
@login_required
def robot_save(team_number):
    team = Team.query.filter_by(number=team_number).first_or_404()
    event = db.session.get(Event, session['event_id'])

    scouting_data = {
        'drive_system': request.form.get('drive_system', ''),
        'ground_intake': request.form.get('ground_intake', '') == 'yes',
        'shooter_system': request.form.get('shooter_system', ''),
        'climb': request.form.get('climb', ''),
    }

    RobotService.save_robot(team.id, event.game_id, scouting_data)
    return redirect(url_for('scouting.robot_list'))


# --- Match Scouting ---

@scouting_bp.route('/matches')
@login_required
def match_list():
    event_id = session['event_id']
    matches = Match.query.filter_by(event_id=event_id).order_by(Match.number).all()
    scout_status = OutcomeService.get_event_match_scout_status(event_id)
    return render_template('scouting/match_list.html', matches=matches, scout_status=scout_status)


@scouting_bp.route('/match/<int:match_id>')
@login_required
def match_teams(match_id):
    match = db.session.get(Match, match_id) or abort(404)

    red_teams = Team.query.filter(Team.number.in_(match.red_teams or [])).all()
    blue_teams = Team.query.filter(Team.number.in_(match.blue_teams or [])).all()

    # Sort to match the order in the JSON arrays
    red_order = {n: i for i, n in enumerate(match.red_teams or [])}
    blue_order = {n: i for i, n in enumerate(match.blue_teams or [])}
    red_teams.sort(key=lambda t: red_order.get(t.number, 0))
    blue_teams.sort(key=lambda t: blue_order.get(t.number, 0))

    scout_counts = OutcomeService.get_match_scout_counts(match_id)
    return render_template('scouting/match_teams.html',
                           match=match, red_teams=red_teams, blue_teams=blue_teams,
                           scout_counts=scout_counts)


@scouting_bp.route('/match/<int:match_id>/team/<int:team_number>')
@login_required
def match_input(match_id, team_number):
    match = db.session.get(Match, match_id) or abort(404)
    team = Team.query.filter_by(number=team_number).first_or_404()

    outcome = OutcomeService.get_outcome(match_id, team.id, session['user_id'])
    data = outcome.scouting_data if outcome else {}
    return render_template('scouting/match_input.html', match=match, team=team, data=data)


@scouting_bp.route('/match/<int:match_id>/team/<int:team_number>', methods=['POST'])
@login_required
def match_save(match_id, team_number):
    match = db.session.get(Match, match_id) or abort(404)
    team = Team.query.filter_by(number=team_number).first_or_404()

    scouting_data = {
        'auton_balls': _parse_int(request.form.get('auton_balls', '')),
        'auton_climb': _parse_int(request.form.get('auton_climb', '')),
        'teleop_balls': _parse_int(request.form.get('teleop_balls', '')),
        'teleop_defense': _parse_int(request.form.get('teleop_defense', '')),
        'teleop_climb': _parse_int(request.form.get('teleop_climb', '')),
    }

    OutcomeService.save_outcome(match_id, team.id, session['user_id'], scouting_data)
    return redirect(url_for('scouting.match_teams', match_id=match_id))


def _parse_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
