from datetime import datetime
from functools import wraps

from flask import session, request, current_app, g
from flask_login import current_user, logout_user
from webapp import login_manager, ctx, babel, db
from webapp.models import User
from flask_babel import _


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@babel.localeselector
def get_locale():
    if not g.get('lang_code', None):
        g.lang_code = request.accept_languages.best_match(current_app.config['LANGUAGES'])
    return g.lang_code


def login_required(roles=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.banned:
                current_user.last_log = datetime.utcnow()
                db.session.commit()
                logout_user()
            if roles and (session['role'] not in roles or 'ME' in roles and current_user.id != 1):
                return login_manager.unauthorized()
            else:
                return fn(*args, **kwargs)

        return decorated_view

    return wrapper


def translate(fatwa_class=None, role=None):
    if fatwa_class:
        if fatwa_class == 'all':
            return _('All')
        if fatwa_class == 'Hadj':
            return _('Hadj')
        elif fatwa_class == 'Salat':
            return _('Salat')
        elif fatwa_class == 'Sawm':
            return _('Sawm')
        elif fatwa_class == 'Zakat':
            return _('Zakat')
    elif role:
        if role == 'Admin':
            return _('Admin')
        elif role == 'Mufti':
            return _('Mufti')
        elif role == 'User':
            return _('User')
