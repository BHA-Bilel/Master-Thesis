from flask import Blueprint, render_template, abort, redirect, current_app, request, url_for, g, session

from webapp import babel, get_locale

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    if session['lang_code']:
        g.lang_code = session['lang_code']
    else:
        g.lang_code = get_locale()
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(403)
def error_404(error):
    if session['lang_code']:
        g.lang_code = session['lang_code']
    else:
        g.lang_code = get_locale()
    return render_template('errors/403.html'), 403


@errors.app_errorhandler(500)
def error_404(error):
    if session['lang_code']:
        g.lang_code = session['lang_code']
    else:
        g.lang_code = get_locale()
    return render_template('errors/500.html'), 500
