from webapp.administration.forms import GeneralForm
from webapp.scheduled_tasks import load_config, save_config

from flask import Blueprint, url_for, render_template, flash, request, redirect, abort, g, current_app, session

from webapp import db
from webapp.scheduled_tasks import sched
from webapp.utils import get_locale, translate
from webapp.models import UserRole, Role, User
from webapp.users.utils import count_all_users, get_all_users, count_banned_users, get_banned_users
from webapp.emails import send_unbanned_email, send_banned_email, send_demote_email, send_promote_email
from webapp.users.forms import *
from flask_login import current_user
from flask_babel import _
from sqlalchemy.exc import IntegrityError
from webapp.utils import login_required

administration = Blueprint('administration', __name__, url_prefix='/<lang_code>/administration')


@administration.route('/<string:role>', methods=['GET', 'POST'])
@login_required(roles=['Admin'])
def all_accounts(role='all'):
    # show all users having that role name (all,Admin,Mufti,User)
    total = count_all_users(role=role)
    if not total:
        abort(404)
    page = request.args.get('page', 1, type=int)
    users, pagination, summary = get_all_users(page=page, role=role)
    return render_template('users/all_accounts.html', users=users, pagination=pagination, total=total, name=role,
                           translated_name=translate(role=role), summary=summary,
                           title=_('all accounts'), route='all_accounts')


@administration.route('/<string:role>/banned', methods=['GET', 'POST'])
@login_required(roles=['Admin'])
def banned_accounts(role='all'):
    # show all users that are banned
    total = count_banned_users(role=role)
    if not total:
        abort(404)
    page = request.args.get('page', 1, type=int)
    users, pagination, summary = get_banned_users(page=page, role=role)
    return render_template('users/all_accounts.html', users=users, pagination=pagination, total=total, summary=summary,
                           title=_('banned accounts'), route='banned_accounts')


@administration.route('/<string:role>/ban_quest', methods=['GET', 'POST'])
@login_required(roles=['Admin'])
def banned_quest_fatwa_accounts(role='all'):
    # show all users that are banned from asking quest_fatwas
    total = count_banned_users(role=role, ban_quest=True)
    if not total:
        abort(404)
    page = request.args.get('page', 1, type=int)
    users, pagination, summary = get_banned_users(page=page, role=role, ban_quest=True)
    return render_template('users/all_accounts.html', users=users, pagination=pagination, total=total, summary=summary,
                           title=_('banned accounts'), route='banned_quest_fatwa_accounts')


@administration.route('/<string:role>/ban_vol', methods=['GET', 'POST'])
@login_required(roles=['Admin'])
def banned_vol_fatwas_accounts(role='all'):
    # show all users that are banned from volunteering vol_fatwas
    total = count_banned_users(role=role, ban_vol=True)
    if not total:
        abort(404)
    page = request.args.get('page', 1, type=int)
    users, pagination, summary = get_banned_users(page=page, role=role, ban_vol=True)
    return render_template('users/all_accounts.html', users=users, pagination=pagination, total=total, summary=summary,
                           title=_('banned accounts'), route='banned_vol_fatwas_accounts')


@administration.route('/<string:username>/promote/<string:role>', methods=['GET', 'POST'])
@login_required(roles=['ME'])
def promote(username, role):
    # route to add role with name=role to a user with username=username

    if username == current_user.username:
        flash(_("You can't demote yourself!"), 'warning')
        return redirect(url_for('users.profile', username=username))

    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    role = Role.query.filter_by(name=role).first()
    if not role:
        abort(404)
    user_role = UserRole(user_id=user.id, role_id=role.id)
    try:
        db.session.add(user_role)
        db.session.commit()
        sched.add_job(send_promote_email, args=[user.pref_lang, role, user.email, user.username])
        flash(_('This user is promoted to %(role)s', role=translate(role=role)), 'success')
    except IntegrityError:
        db.session.rollback()
        flash(_("This user is already %(role)s!", role=translate(role=role)), 'warning')
    return redirect(url_for('users.profile', username=username))


@administration.route('/<string:username>/demote/<string:role>', methods=['GET', 'POST'])
@login_required(roles=['ME'])
def demote(username, role):
    if username == current_user.username:
        flash(_("You can't demote yourself!"), 'warning')
        return redirect(url_for('users.profile', username=username))

    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)

    role = Role.query.filter_by(name=role).first()
    if not role:
        abort(404)

    user_role = UserRole.query.filter_by(user_id=user.id, role_id=role.id).first()
    if not user_role:
        flash(_("This user isn't a %(role)s!", role=translate(role=role)), 'warning')
    else:
        db.session.delete(user_role)
        db.session.commit()
        sched.add_job(send_demote_email, args=[user.pref_lang, role, user.email, user.username])
        flash(_('This user is no longer %(role)s', role=translate(role=role)), 'success')
    return redirect(url_for('users.profile', username=username))


@administration.route('/<string:username>/ban')
@login_required(roles=['Admin', 'Mufti'])
def ban_user(username):
    # route to ban/un-ban user
    if username == current_user.username:
        flash(_("You can't ban yourself!"), 'warning')
        return redirect(url_for('users.profile', username=username))

    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    if user.id == 1:
        flash(_("You can't ban the creator of the website!"), 'danger')
        return redirect(url_for('users.profile', username=username))

    if current_user.id != 1:
        admin_role = Role.query.filter_by(name='Admin').first()
        mufti_role = Role.query.filter_by(name='Mufti').first()
        roles = UserRole.query.filter_by(user_id=user.id).all()
        for role in roles:
            if role.id == admin_role.id:
                flash(_("This user is also an admin, you can't ban him!"), 'warning')
                return redirect(url_for('users.profile', username=username))

            elif role.id == mufti_role.id:
                flash(_("This user is a mufti, you can't ban him!"), 'warning')
                return redirect(url_for('users.profile', username=username))

    if user.banned:
        user.banned = False
        db.session.commit()
        flash(_('This user is no longer banned and can access his account again'), 'success')
        sched.add_job(send_unbanned_email, args=[user.pref_lang, user.email, user.username])
    else:
        user.banned = True
        db.session.commit()
        flash(_('This user is now banned and can no longer access his account'), 'success')
        sched.add_job(send_banned_email, args=[user.pref_lang, user.email, user.username])

    return redirect(url_for('users.profile', username=username))


@administration.route('/<string:username>/ban_quest')
@login_required(roles=['Admin', 'Mufti'])
def ban_user_quest(username):
    # route to ban/un-ban user from asking questions
    if username == current_user.username:
        flash(_("You can't restrict yourself!"), 'warning')
        return redirect(url_for('users.profile', username=username))

    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    if user.id == 1:
        flash(_("You can't restrict the creator of the website!"), 'danger')
        return redirect(url_for('users.profile', username=username))

    if current_user.id != 1:
        admin_role = Role.query.filter_by(name='Admin').first()
        mufti_role = Role.query.filter_by(name='Mufti').first()
        roles = UserRole.query.filter_by(user_id=user.id).all()
        for role in roles:
            if role.id == admin_role.id:
                flash(_("This user is also an admin, you can't restrict him!"), 'warning')
                return redirect(url_for('users.profile', username=username))
            elif role.id == mufti_role.id:
                flash(_("This user is a mufti, you can't restrict him!"), 'warning')
                return redirect(url_for('users.profile', username=username))

    if user.ban_quest:
        user.ban_quest = False
        user.deleted_quest = 0
        db.session.commit()
        flash(_('This user is no longer restricted to ask questions'), 'success')
        sched.add_job(send_unbanned_email, args=[user.pref_lang, user.email, user.username])
    else:
        user.ban_quest = True
        db.session.commit()
        flash(_('This user is now restricted from asking questions'), 'success')
        sched.add_job(send_banned_email, args=[user.pref_lang, user.email, user.username])

    return redirect(url_for('users.profile', username=username))


@administration.route('/<string:username>/ban_vol')
@login_required(roles=['Admin', 'Mufti'])
def ban_user_vol(username):
    # route to ban/un-ban user from volunteering fatwas
    if username == current_user.username:
        flash(_("You can't restrict yourself!"), 'warning')
        return redirect(url_for('users.profile', username=username))

    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    if user.id == 1:
        flash(_("You can't restrict the creator of the website!"), 'danger')
        return redirect(url_for('users.profile', username=username))

    if current_user.id != 1:
        admin_role = Role.query.filter_by(name='Admin').first()
        mufti_role = Role.query.filter_by(name='Mufti').first()
        roles = UserRole.query.filter_by(user_id=user.id).all()
        for role in roles:
            if role.id == admin_role.id:
                flash(_("This user is also an admin, you can't restrict him!"), 'warning')
                return redirect(url_for('users.profile', username=username))
            elif role.id == mufti_role.id:
                flash(_("This user is a mufti, you can't restrict him!"), 'warning')
                return redirect(url_for('users.profile', username=username))

    if user.ban_vol:
        user.ban_vol = False
        user.deleted_vol = 0
        db.session.commit()
        flash(_('This user is no longer restricted to volunteer fatwas'), 'success')
        sched.add_job(send_unbanned_email, args=[user.pref_lang, user.email, user.username])
    else:
        user.ban_vol = True
        db.session.commit()
        flash(_('This user is now restricted from volunteering fatwas'), 'success')
        sched.add_job(send_banned_email, args=[user.pref_lang, user.email, user.username])

    return redirect(url_for('users.profile', username=username))


@administration.route('/general', methods=['get', 'post'])
@login_required(roles=['ME'])
def general():
    form = GeneralForm(meta={'locales': get_locale()})
    config = load_config()
    if form.validate_on_submit():
        config['min_data_per_class'] = int(form.min_data_per_class.data)
        config['del_quest_ban'] = int(form.del_quest_ban.data)
        config['del_vol_ban'] = int(form.del_vol_ban.data)
        save_config(config=config)
        return redirect(url_for('administration.general'))
    elif request.method == 'GET':
        form.mincltrain_data_per_class.data = config['min_data_per_class']
        form.del_quest_ban.data = config['del_quest_ban']
        form.del_vol_ban.data = config['del_vol_ban']
        return render_template('admin/general.html', form=form)


# ----------------------------------------------------------------------------------------------------------------

@administration.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@administration.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@administration.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)
