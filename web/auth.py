from functools import wraps

from flask import session, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('main.login'))
        if not session.get('event_id'):
            return redirect(url_for('main.select_event'))
        return f(*args, **kwargs)
    return decorated
