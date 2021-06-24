from flask import Blueprint, render_template, request, g, url_for, redirect, current_app, abort, flash, Markup

from flask_sqlalchemy import Pagination

from webapp import db
from webapp.fatwas.utils import get_fatwa_summary
from webapp.quest_fatwas.utils import count_active_questions, count_answered_questions
from flask_babel import _
from flask_login import current_user

main = Blueprint('main', __name__, url_prefix='/<lang_code>/main')


@main.route('/about')
def about():
    # todo change summary
    fatwas_sum = get_fatwa_summary()
    active_question_sum = count_active_questions()
    answered_question_sum = count_answered_questions()
    return render_template('main/about.html', title=_('About'), fatwas_sum=fatwas_sum, answered_question_sum=answered_question_sum,
                           active_question_sum=active_question_sum)


@main.route('/index')
def index():
    next_page = request.args.get('next')
    if next_page:
        g.lang_code = current_user.pref_lang
        return redirect(next_page)
    else:
        g.lang_code = request.accept_languages.best_match(current_app.config['LANGUAGES'])
    return redirect(url_for('main.home'))


@main.route('/', methods=['GET', 'POST'])
def home():
    # todo change home page to show a welcome message only
    if current_user.is_authenticated:
        if request.args.get('changed'):
            current_user.pref_lang = g.lang_code
            db.session.commit()
        # if not current_user.ver_em:
        #     msg = _('You need to verify your email in order to benefit of you privileges') + Markup(
        #         f'<a href={url_for("users.confirm_request")} class="alert-link">' + _(' Resend confirmation link') + '</a>')
        #     flash(message=msg, category='warning')
    return render_template('main/home.html')


# --------------------------------------------------------------------------------------------------------


@main.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@main.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@main.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)
