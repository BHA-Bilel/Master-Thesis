from datetime import datetime

from flask import Blueprint, url_for, render_template, flash, request, redirect, abort, g, current_app, session

from webapp import db, bcrypt
from webapp.scheduled_tasks import sched
from webapp.utils import get_locale, translate
from webapp.models import UserRole, Role, User, ReportUser
from webapp.users.utils import log_in, register_user, count_all_users, get_all_users, count_banned_users, get_banned_users, get_mufti_summary, \
    get_user_summary
from webapp.emails import send_reset_email, send_verify_email, send_request_email
from webapp.users.forms import *
from flask_login import current_user, logout_user
from flask_babel import _
from sqlalchemy.exc import IntegrityError
from webapp.utils import login_required

users = Blueprint('users', __name__, url_prefix='/<lang_code>/users')


@users.route('/mufti_request', methods=['get', 'post'])
@login_required(roles=['User'])
def request_mufti():
    # route for users to request a promotion of a mufti:
    role = Role.query.filter_by(name='Mufti').first()
    user_role = UserRole.query.filter_by(user_id=current_user.id, role_id=role.id).first()
    if user_role:
        flash(_('You are already a mufti, login without @User to access your mufti privileges'), 'info')
        return redirect(url_for('users.profile', username=current_user.username))

    form = RequestMuftiForm()
    if form.validate_on_submit():
        sched.add_job(send_request_email, args=[current_user.username, form.proof.file, form.detail.data])
        flash(_('Your request has been sent to the administration, and will be processed later'), 'info')
        return redirect(url_for(_('users.profile', username=current_user.username)))
    return render_template('users/request.html', form=form, title=_('Become a mufti'))


@users.route('/<string:username>/profile', methods=['get', 'post'])
def profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    if user.banned:
        if not current_user.is_authenticated:
            abort(404)
        elif session['role'] != 'Admin':
            abort(404)
    user_role = Role.query.filter_by(name='User').first()
    mufti_role = Role.query.filter_by(name='Mufti').first()
    roles = UserRole.query.filter_by(user_id=user.id).first()
    user_summary = None
    mufti_summary = None
    for role in roles:
        if role.role_id == user_role.id:
            user_summary = get_user_summary(user_id=user.id)
        elif role.role_id == mufti_role.id:
            mufti_summary = get_mufti_summary(mufti_id=user.id)
    return render_template('users/profile.html', title=_('Profile'), username=username, user_summary=user_summary, mufti_summary=mufti_summary)


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.fname = form.fname.data
        current_user.lname = form.lname.data
        if current_user.email != form.email.data:
            current_user.email = form.email.data
            current_user.ver_em = False
            sched.add_job(send_verify_email)
            flash(_('An email has been sent with instructions to verify your new email address'), 'info')
        db.session.commit()
        flash(_('Your account has been updated!'), 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.fname.data = current_user.fname
        form.lname.data = current_user.lname
        form.email.data = current_user.email
    return render_template('users/account.html', form=form, title=_('Account'))


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(_('You are already logged in!'), 'info')
        return redirect(url_for('main.home'))
    else:
        form = LoginForm(meta={'locales': get_locale()})
        if form.validate_on_submit():
            id = log_in(form.username.data, form.password.data, request.form.get('remember'))
            if id > 0:
                next_page = request.args.get('next')
                flash(_('logged in as %(role)s %(username)s',
                        role=translate(role=session['role']), username=form.username.data), 'success')
                return redirect(url_for('main.index', next_page=next_page, lang_code=current_user.pref_lang)) if next_page else redirect(
                    url_for('main.home', lang_code=current_user.pref_lang, _method="GET"))
            elif id == -1:
                flash(_('User does not exist !'), 'danger')
            elif id == -2:
                flash(_('Your account is banned!'), 'danger')
            elif id == -3:
                flash(_('You do not have this privilege!'), 'danger')
            else:
                flash(_('Wrong credential !'), 'danger')
        return render_template('users/login.html', form=form, title=_('Login'))


@users.route('/logout', methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        current_user.last_log = datetime.utcnow()
        db.session.commit()
        logout_user()
        flash(_('You are now logged out'), 'success')
        return redirect(url_for('users.login'))
    else:
        flash(_("You're not logged in!"), 'warning')
        return redirect(url_for('users.login'))


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_id = register_user(form.fname.data, form.lname.data, form.username.data, password_hash, form.email.data)
        flash(_('%(username)s created successfully', username=form.username.data), 'success')
        sched.add_job(send_verify_email, args=[user_id, form.username.data, form.email.data])
        flash(_('An email has been sent with instructions to verify your account'), 'info')
        return redirect(url_for('users.login', _method="GET"))
    return render_template('users/register.html', form=form, title=_('Register'))


@users.route('/confirm_email')
@login_required
def confirm_request():
    if current_user.ver_em:
        flash(_('Your account is already verified!'), 'info')
        return redirect(url_for('main.home'))
    else:
        sched.add_job(send_verify_email)
        flash(_('An email has been sent with instructions to verify your account'), 'info')
        return redirect(url_for('main.home'))


@users.route('/confirm_email/<token>')
def confirm_email(token):
    user = User.verify_token(token=token)
    if user is None:
        flash(_('That is an invalid or expired token'), 'warning')
        return redirect(url_for('users.confirm_request'))
    else:
        user.ver_em = True
        db.session.commit()
        flash(_('Your account is validated successfully, you can now use your account privileges'), 'success')
        return redirect(url_for('main.home'))


@users.route('/change_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        sched.add_job(send_reset_email, args=[current_user])
        flash(_('An email has been sent with instructions to change your password'), 'info')
        return redirect(url_for('users.home'))

    form = RequestResetForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        sched.add_job(send_reset_email, args=[user])
        flash(_('An email has been sent with instructions to reset your password'), 'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_request.html', title=_('Reset Password'), form=form)


@users.route('/change_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        flash(_('That is an invalid or expired token'), 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = password_hash
        db.session.commit()
        flash(_('Your password has been updated! You are now able to log in'), 'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_token.html', title=_('Reset Password'), form=form)


# ----------------------------------------------------------------------------------------------------------------


@users.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@users.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@users.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)
