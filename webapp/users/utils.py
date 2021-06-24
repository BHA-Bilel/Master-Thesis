from datetime import datetime

from flask_login import login_user, current_user

from webapp import bcrypt, db
from flask import session
from webapp.models import User, Role, UserRole, QuestFatwa, Fatwa, VolFatwa, DelQuestion, DelVolFatwa, DelFatwa


def count_all_users(role):
    if role == 'all':
        users = User.query.count()
    else:
        this_role = Role.query.filter_by(name=role).first()
        if not this_role:
            return None
        users = User.query.filter_by(user_role=this_role.id).count()
    return users


def get_all_users(page, role):
    user_role = Role.query.filter_by(name='User').first()
    mufti_role = Role.query.filter_by(name='Mufti').first()
    admin_role = Role.query.filter_by(name='Admin').first()
    summary = dict()
    if role == 'all':
        users = User.query.order_by(User.id.desc()).paginate(per_page=20, page=page, error_out=True)
        for user in users:
            user_summary = None
            mufti_summary = None
            is_admin = False
            for urole in user.roles:
                if urole.id == admin_role.id:
                    is_admin = True
                if urole.role_id == user_role.id:
                    user_summary = get_user_summary(user_id=user.id)
                elif urole.role_id == mufti_role.id:
                    mufti_summary = get_mufti_summary(mufti_id=user.id)
            summary[user.id] = {'is_admin': is_admin, 'user_summary': user_summary,
                                'mufti_summary': mufti_summary}
        pagination = users
    else:
        urole = Role.query.filter_by(name=role).first()
        if not urole:
            return None
        pagination = UserRole.query.filter_by(role_id=urole.id).order_by(UserRole.user_id.desc()).paginate(per_page=20, page=page, error_out=True)
        users = User.query.order_by(User.id.desc()).filter(User.id.distinct(), User.id.in_([pg.user_id for pg in pagination])).all()
        all_users_roles = UserRole.query.filter(UserRole.user_id.in_([user.id for user in users])).all()
        for users_roles in all_users_roles:
            if not summary[users_roles.user_id]:
                summary[users_roles.user_id] = {}
            if users_roles.role_id == admin_role.id:
                summary[users_roles.user_id]['is_admin'] = True
            if users_roles.role_id == user_role.id:
                summary[users_roles.user_id]['user_summary'] = get_user_summary(user_id=users_roles.user_id)
            elif users_roles.role_id == mufti_role.id:
                summary[users_roles.user_id]['mufti_summary'] = get_mufti_summary(mufti_id=users_roles.user_id)

    return users, pagination, summary


def get_banned_users(page, role, ban_quest=None, ban_vol=None):
    # user_role = Role.query.filter_by(name='User').first()
    # mufti_role = Role.query.filter_by(name='Mufti').first()
    summary = dict()
    if ban_quest is None and ban_vol is None:
        # could be user or mufti
        users = User.query.filter_by(banned=True).order_by(User.id.desc()).paginate(per_page=20, page=page, error_out=True)
        for user in users:
            user_summary = None
            mufti_summary = None
            for urole in user.roles:
                if urole.role_id == user_role.id:
                    user_summary = get_user_summary(user_id=user.id)
                elif urole.role_id == mufti_role.id:
                    mufti_summary = get_mufti_summary(mufti_id=user.id)
            summary[user.id] = {'user_summary': user_summary,
                                'mufti_summary': mufti_summary}
        pagination = users
    else:
        users = None
        the_role = Role.query.filter_by(name=role).first()
        if ban_quest:
            users = User.query.filter_by(ban_quest=True).order_by(User.id.desc()).paginate(per_page=20, page=page, error_out=True)
        elif ban_vol:
            users = User.query.filter_by(ban_vol=True).order_by(User.id.desc()).paginate(per_page=20, page=page, error_out=True)
        for user in users:
            user_summary = get_user_summary(user_id=user.id)
            summary[user.id] = {'user_summary': user_summary}
        pagination = users
    return users, pagination, summary


def count_banned_users(role, ban_quest=None, ban_vol=None):
    count = None
    if role == 'all':
        if ban_quest is None and ban_vol is None:
            count = User.query.filter_by(banned=True).count()
        elif ban_quest:
            count = User.query.filter_by(ban_quest=True).count()
        elif ban_vol:
            count = User.query.filter_by(ban_vol=True).count()
    else:
        the_role = Role.query.filter_by(name='User').first()
        if ban_quest is None and ban_vol is None:
            count = User.query.filter_by(user_role=the_role.id, banned=True).count()
        elif ban_quest:
            count = User.query.filter_by(user_role=the_role.id, ban_quest=True).count()
        elif ban_vol:
            count = User.query.filter_by(user_role=the_role.id, ban_vol=True).count()
    return count


def get_user_summary(user_id):
    asked_questions = QuestFatwa.query.filter(QuestFatwa.user_id == user_id, QuestFatwa.mufti_id == None).count()
    answered_questions = QuestFatwa.query.filter(QuestFatwa.user_id == user_id, QuestFatwa.mufti_id != None).count()
    volunteered_vol_fatwas = VolFatwa.query.filter_by(user_id=user_id).count()
    deleted_questions = DelQuestion.query.filter_by(user_id=user_id).count()
    deleted_vol_fatwas = DelVolFatwa.query.filter_by(user_id=user_id).count()
    user_summary = {
        'asked_questions': asked_questions,
        'answered_questions': answered_questions,
        'volunteered_vol_fatwas': volunteered_vol_fatwas,
        'deleted_questions': deleted_questions,
        'deleted_vol_fatwas': deleted_vol_fatwas
    }
    return user_summary


def get_mufti_summary(mufti_id):
    fatwas = Fatwa.query.filter_by(mufti_id=mufti_id).count()
    answered_questions = QuestFatwa.query.filter_by(mufti_id=mufti_id).count()
    deleted_fatwas = DelFatwa.query.filter_by(mufti_id=mufti_id).count()
    mufti_summary = {
        'fatwas': fatwas,
        'answered_questions': answered_questions,
        'deleted_fatwas': deleted_fatwas}
    return mufti_summary


def log_in(username, password, remember):
    username_at = username.split('@')
    user = User.query.filter_by(username=username_at[0]).first()
    if user:
        check = bcrypt.check_password_hash(user.password, password)
        if check:
            if user.banned:
                return -2
            if len(username_at) == 2:
                role = Role.query.filter_by(name=username_at[1]).first()
                if role and user.id in [user_role.user_id for user_role in role.owners]:
                    session['role'] = role.name
                else:
                    return -3
            else:
                if 'Admin' in user.roles:
                    session['role'] = 'Admin'
                elif 'Mufti' in user.roles:
                    session['role'] = 'Mufti'
                elif 'User' in user.roles:
                    session['role'] = 'User'
            user.last_log = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=remember)
            return user.id
        else:
            return 0
    else:
        return -1


def register_user(fname, lname, username, password, email):
    user = User(fname=fname, lname=lname, username=username, password=password, email=email)
    db.session.add(user)
    db.session.commit()

    role = Role.query.filter_by(name='User').first()
    user_role = UserRole(role_id=role.id, user_id=user.id)

    db.session.add(user_role)
    db.session.commit()

    return user.id
