from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response

from web.extensions import db
from web.services.user_service import UserService

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return redirect(url_for('main.home'))


@main_bp.route('/home')
def home():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))
    if not session.get('event_id'):
        return redirect(url_for('main.select_event'))
    return render_template('home.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    # POST — create new user
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            flash('Please enter a name.', 'error')
            return redirect(url_for('main.login'))

        user = UserService.create(username)
        if not user:
            flash('That name is already taken.', 'error')
            return redirect(url_for('main.login'))

        return _set_user_session(user)

    # GET with select_user param — select existing user
    select_user_id = request.args.get('select_user', type=int)
    if select_user_id:
        user = UserService.get(select_user_id)
        if user:
            return _set_user_session(user)

    # GET — check for remembered user cookie
    remembered_id_str = request.cookies.get('scout_user_id')
    remembered_id = int(remembered_id_str) if remembered_id_str else None
    if remembered_id and not session.get('user_id'):
        user = UserService.get(remembered_id)
        if user:
            return _set_user_session(user)

    users = UserService.get_all()
    return render_template('login.html', users=users)


@main_bp.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect(url_for('main.login')))
    response.delete_cookie('scout_user_id')
    return response


@main_bp.route('/events')
def select_event():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))

    event_id = request.args.get('event_id', type=int)
    if event_id:
        from web.models.event import Event
        event = db.session.get(Event, event_id)
        if event:
            session['event_id'] = event.id
            session['event_name'] = event.name
            flash(f'Selected event: {event.name}', 'success')
            return redirect(url_for('main.index'))

    from web.models.event import Event
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('events.html', events=events)


def _set_user_session(user):
    session['user_id'] = user.id
    session['username'] = user.username
    session['team_id'] = user.team_id
    response = make_response(redirect(url_for('main.select_event')))
    response.set_cookie('scout_user_id', str(user.id), max_age=60 * 60 * 24 * 365)
    return response
