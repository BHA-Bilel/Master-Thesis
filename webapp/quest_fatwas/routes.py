from flask import Blueprint, url_for, render_template, flash, request, redirect, abort, g, current_app, session, Response
from flask_login import current_user

from webapp import User, db
from webapp.fatwas.forms import FatwaForm
from webapp.models import DelQuestion, DelFatwa
from webapp.quest_fatwas.forms import QuestFatwaForm
from webapp.quest_fatwas.utils import *
from webapp.utils import login_required, get_locale, translate

from flask_babel import _

from webapp.websites.utils import zipfiles

quest_fatwas = Blueprint('quest_fatwas', __name__, url_prefix='/<lang_code>/quest_fatwas')


@quest_fatwas.route('/<string:name>/asked', methods=['GET', 'POST'])
@login_required(roles=['Admin', 'Mufti'])
def asked_quest_fatwas(name='all'):
    page = request.args.get('page', 1, type=int)
    total = count_all_quest_fatwas(name=name, answered=False)
    if not total:
        abort(404)
    fatwas = get_all_quest_fatwas(name=name, page=page, answered=False)
    usernames = dict()
    for fatwa in fatwas.items:
        if fatwa.user_id not in usernames:
            user = User.query.get(fatwa.user_id)
            usernames[fatwa.user_id] = user.username

    return render_template('quest_fatwas/all_quest_fatwas.html', title=_('questions'), fatwas=fatwas,
                           name=name, translated_name=translate(fatwa_class=name),
                           total=total, usernames=usernames, route='asked_quest_fatwas')


@quest_fatwas.route('/<string:name>/deleted', methods=['GET', 'POST'])
@login_required(roles=['Admin'])
def del_quest_fatwas():
    page = request.args.get('page', 1, type=int)
    total = count_del_quest_fatwas()
    if not total:
        abort(404)
    fatwas = get_del_quest_fatwas(page=page)
    usernames = dict()
    for fatwa in fatwas.items:
        if fatwa.user_id not in usernames:
            user = User.query.get(fatwa.user_id)
            usernames[fatwa.user_id] = user.username
        if fatwa.deleter_id not in usernames:
            deleter = User.query.get(fatwa.deleter_id)
            usernames[fatwa.deleter_id] = deleter.username

    return render_template('quest_fatwas/del_quest_fatwas.html', title=_('deleted questions'), fatwas=fatwas,
                           total=total, usernames=usernames, route='del_quest_fatwas')


@quest_fatwas.route('/<string:name>/<string:name>', methods=['GET', 'POST'])
def answered_quest_fatwas(name='all'):
    page = request.args.get('page', 1, type=int)
    total = count_all_quest_fatwas(name=name, answered=True)
    if not total:
        abort(404)
    fatwas = get_all_quest_fatwas(name=name, page=page, answered=True)
    usernames = dict()
    for fatwa in fatwas.items:
        if fatwa.user_id not in usernames:
            user = User.query.get(fatwa.user_id)
            usernames[fatwa.user_id] = user.username
        if fatwa.mufti_id not in usernames:
            mufti = User.query.get(fatwa.mufti_id)
            usernames[fatwa.mufti_id] = mufti.username
    return render_template('quest_fatwas/all_quest_fatwas.html', title=_('fatwas'), translated_name=translate(fatwa_class=name),
                           fatwas=fatwas, name=name, total=total, usernames=usernames, route='answered_quest_fatwas')


@quest_fatwas.route('/users/<string:username>/<string:name>/asked', methods=['GET', 'POST'])
@login_required
def asked_user_quest_fatwas(username, name='all'):
    if session['role'] == 'User' and current_user.username != username:
        abort(403)
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    # show unanswered quest_fatwas for that user
    page = request.args.get('page', 1, type=int)
    total = count_user_quest_fatwas(user_id=user.id, answered=False, name=name)
    fatwas = get_user_quest_fatwas(user_id=user.id, page=page, answered=False, name=name)
    return render_template('quest_fatwas/all_quest_fatwas.html', title=_('questions'), fatwas=fatwas,
                           name=name, translated_name=translate(fatwa_class=name),
                           total=total, username=username, route='asked_user_quest_fatwas')


@quest_fatwas.route('/users/<string:username>/<string:name>/deleted', methods=['GET', 'POST'])
@login_required(roles=['Admin'])
def user_del_quest_fatwas(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    # show deleted quest_fatwas for that user
    page = request.args.get('page', 1, type=int)
    total = count_del_quest_fatwas(user_id=user.id)
    fatwas = get_del_quest_fatwas(page=page, user_id=user.id)
    usernames = dict()
    usernames[user.id] = user.username
    for fatwa in fatwas.items:
        if fatwa.deleter_id not in usernames:
            deleter = User.query.get(fatwa.deleter_id)
            usernames[fatwa.deleter_id] = deleter.username
    return render_template('quest_fatwas/del_quest_fatwas.html', title=_('deleted questions'), fatwas=fatwas,
                           total=total, usernames=usernames, route='user_del_quest_fatwas')


@quest_fatwas.route('/users/<string:username>/<string:name>', methods=['GET', 'POST'])
def answered_user_quest_fatwas(username, name='all'):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    # show answered quest_fatwas for that user
    page = request.args.get('page', 1, type=int)
    total = count_user_quest_fatwas(user_id=user.id, answered=True, name=name)
    fatwas = get_user_quest_fatwas(user_id=user.id, page=page, answered=True, name=name)
    usernames = dict()
    usernames[user.id] = user.username
    for fatwa in fatwas.items:
        if fatwa.mufti_id not in usernames:
            mufti = User.query.get(fatwa.mufti_id)
            usernames[fatwa.mufti_id] = mufti.username
    return render_template('quest_fatwas/all_quest_fatwas.html', title=_('questions'), fatwas=fatwas, name=name,
                           translated_name=translate(fatwa_class=name),
                           total=total, usernames=usernames, route='answered_user_quest_fatwas')


@quest_fatwas.route('/muftis/<string:username>/<string:name>', methods=['GET', 'POST'])
def mufti_quest_fatwas(username, name='all'):
    mufti = User.query.filter_by(username=username).first()
    if not mufti:
        abort(404)
    # show answered quest_fatwas by that mufti
    page = request.args.get('page', 1, type=int)
    total = count_mufti_quest_fatwas(mufti_id=mufti.id, name=name)
    fatwas = get_mufti_quest_fatwas(mufti_id=mufti.id, page=page, name=name)
    usernames = dict()
    usernames[mufti.id] = mufti.username
    for fatwa in fatwas.items:
        if fatwa.user_id not in usernames:
            user = User.query.get(fatwa.user_id)
            usernames[fatwa.user_id] = user.username
    return render_template('quest_fatwas/all_quest_fatwas.html', title=_('questions'), fatwas=fatwas,
                           name=name, translated_name=translate(fatwa_class=name),
                           total=total, usernames=usernames, route='mufti_quest_fatwas')


@quest_fatwas.route('/add', methods=['GET', 'POST'])
@login_required(roles=['User'])
def add_quest_fatwa():
    if current_user.ban_quest:
        flash(_('Unfortunately, you are banned from asking questions'), 'warning')
        return redirect(url_for('main.home'))
    if not current_user.ver_em:
        flash(_('You need to verify your email in order to ask new questions!'), 'warning')
        return redirect(url_for('main.home'))
    form = QuestFatwaForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        quest_fatwa = QuestFatwa(question=form.question, class_id=form.fatwa_class.id, anonym=form.anonym.data, user_id=current_user.id)
        db.session.add(quest_fatwa)
        db.session.commit()
        flash(_('Question added successfully!'), 'success')
        return redirect(url_for('quest_fatwas.quest_fatwa', id=quest_fatwa.id))
    elif request.method == 'GET':
        question = request.args.get('question', '', str)
        form.question.data = question
    flash(_('Please consider checking similar questions before asking a new one'), 'info')
    return render_template('quest_fatwas/change.html', title=_('new question'), form=form, legend=_('New question'))


@quest_fatwas.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required(roles=['Mufti', 'User'])
def edit_quest_fatwa(id):
    quest_fatwa = QuestFatwa.query.get_or_404(id)
    answered = quest_fatwa.mufti_id
    if answered:
        if session['role'] == 'User':
            if quest_fatwa.user_id == current_user.id:
                flash(_('You can not edit this question because it is already answered!'), 'warning')
                return redirect(url_for('quest_fatwas.quest_fatwa', id=id))
            else:
                abort(403)
        if session['role'] == 'Mufti' and quest_fatwa.mufti_id != current_user.id:
            abort(403)
    else:
        if session['role'] == 'User' and quest_fatwa.user_id != current_user.id:
            abort(403)
        if session['role'] == 'Mufti':
            abort(403)

    if not current_user.ver_em:
        flash(_('You need to verify your email in order to edit this question!'), 'warning')
        return redirect(url_for('quest_fatwas.quest_fatwa', id=id))

    if current_user.id == quest_fatwa.user_id and current_user.ban_quest:
        flash(_('Unfortunately, you no longer have any control of your questions'), 'warning')
        return redirect(url_for('main.home'))

    if session['role'] == 'User':
        form = QuestFatwaForm(meta={'locales': get_locale()})
        if form.validate_on_submit():
            quest_fatwa.class_id = form.fatwa_class.id
            quest_fatwa.anonym = form.anonym.data
            quest_fatwa.email_notif = form.email_notif.data
            quest_fatwa.question = form.question.data
            db.session.commit()
            flash(_('Question has been updated!'), 'success')
            return redirect(url_for('quest_fatwas.quest_fatwa', id=quest_fatwa.id))
        elif request.method == 'GET':
            form.fatwa_class.id = quest_fatwa.class_id
            form.anonym.data = quest_fatwa.anonym
            form.email_notif.data = quest_fatwa.email_notif
            form.question.data = quest_fatwa.question
        return render_template('quest_fatwas/change.html', title=_('edit question'), form=form, legend=_('Edit question'))
    elif session['role'] == 'Mufti':
        form = FatwaForm(meta={'locales': get_locale()})
        if form.validate_on_submit():
            quest_fatwa.question = form.question.data
            quest_fatwa.answer = form.answer.data
            quest_fatwa.class_id = form.fatwa_class.id
            db.session.commit()
            flash(_('Fatwa has been updated!'), 'success')
            return redirect(url_for('quest_fatwas.quest_fatwa', id=quest_fatwa.id))
        elif request.method == 'GET':
            form.fatwa_class.id = quest_fatwa.class_id
            form.question.data = quest_fatwa.question
            form.answer.data = quest_fatwa.answer
        return render_template('fatwas/change.html', title=_('edit fatwa'), fatwa=quest_fatwa, form=form, legend=_('Edit fatwa'))


@quest_fatwas.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_quest_fatwa(id):
    quest_fatwa = QuestFatwa.query.get_or_404(id)

    answered = quest_fatwa.mufti_id
    if answered:
        if session['role'] == 'User':
            if quest_fatwa.user_id == current_user.id:
                flash(_('You can not delete this question because it is already answered!'), 'warning')
                return redirect(url_for('quest_fatwas.quest_fatwa', id=id))
            else:
                abort(403)
        if session['role'] == 'Mufti' and quest_fatwa.mufti_id != current_user.id:
            abort(403)
    else:
        if session['role'] == 'User' and quest_fatwa.user_id != current_user.id:
            abort(403)

    if not current_user.ver_em:
        flash(_('You need to verify your email in order to delete this question!'), 'warning')
        return redirect(url_for('quest_fatwas.quest_fatwa', id=id))

    if current_user.id == quest_fatwa.user_id and current_user.ban_quest:
        flash(_('Unfortunately, you no longer have any control of your questions'), 'warning')
        return redirect(url_for('main.home'))

    if answered:
        if session['role'] == 'Admin' and quest_fatwa.mufti_id != current_user.id:
            del_fatwa = DelFatwa(mufti_id=quest_fatwa.mufti_id, admin_id=current_user.id, question=quest_fatwa.question, answer=quest_fatwa.answer)
            db.session.add(del_fatwa)
        db.session.delete(quest_fatwa)
        db.session.commit()
        flash(_('Fatwa has been deleted!'), 'success')
    else:
        if session['role'] == 'User':
            db.session.delete(quest_fatwa)
            db.session.commit()
        elif (session['role'] == 'Admin' or session['role'] == 'Mufti') and quest_fatwa.user_id != current_user.id:
            del_question = DelQuestion(question=quest_fatwa.question, user_id=quest_fatwa.user_id, deleter_id=current_user.id)
            db.session.add(del_question)
            db.session.delete(quest_fatwa)
            db.session.commit()
        flash(_('Question has been deleted!'), 'success')
    return redirect(url_for('main.home'))


@quest_fatwas.route('/<int:id>')
def quest_fatwa(id):
    quest_fatwa = QuestFatwa.query.get_or_404(id)
    usernames = dict()

    if not quest_fatwa.mufti_id:
        if not current_user.is_authenticated:
            abort(403)
        if current_user.is_authenticated and session['role'] == 'User' and quest_fatwa.user_id != current_user.id:
            abort(403)
    else:
        mufti = User.query.filter_by(id=quest_fatwa.mufti_id).first()
        usernames[mufti.id] = quest_fatwa.mufti_id

    if not quest_fatwa.anonym or current_user.is_authenticated and session['role'] == 'Admin':
        user = User.query.filter_by(id=quest_fatwa.user_id).first()
        usernames[user.id] = user.username
    if quest_fatwa.mufti_id:
        title = _('Fatwa')
    else:
        title = _('Question')
    return render_template('quest_fatwas/quest_fatwa.html', title=title, fatwa=quest_fatwa, usernames=usernames)


@quest_fatwas.route('/<int:id>/answer', methods=['GET', 'POST'])
@login_required(roles=['Mufti'])
def answer_quest_fatwa(id):
    quest_fatwa = QuestFatwa.query.get_or_404(id)

    if quest_fatwa.mufti_id:
        flash(_('This question is already answered!'), 'warning')
        return redirect(url_for('quest_fatwas.quest_fatwa', id=quest_fatwa.id))

    if not current_user.ver_em:
        flash(_('You need to verify your email in order to answer this question!'), 'warning')
        return redirect(url_for('main.home'))

    form = FatwaForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        quest_fatwa.question = form.question.data
        quest_fatwa.answer = form.answer.data
        quest_fatwa.class_id = form.fatwa_class.id
        db.session.commit()
        flash(_('Thank you for answering this question!'), 'success')
        return redirect(url_for('quest_fatwas.quest_fatwa', id=quest_fatwa.id))
    elif request.method == 'GET':
        form.fatwa_class.id = quest_fatwa.class_id
        form.question.data = quest_fatwa.question
        form.answer.data = quest_fatwa.answer
    return render_template('fatwas/change.html', title=_('answer question'), fatwa=quest_fatwa, form=form, legend=_('Answer question'))


@quest_fatwas.route('/<string:name>/download', methods=['POST'])
@login_required(roles=['ME'])
def download_quest_fatwas(name='all'):
    if name == 'all':
        files = []
        all_classes = FatwaClass.query.all()
        for cl in all_classes:
            files.append(backup_quest_fatwas_csv(cl=cl))
        file = zipfiles(files=files)
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            abort(404)
        file = backup_quest_fatwas_csv(cl=cl)
    flash(_('Corpus exported to your machine'), 'success')
    return Response(file, mimetype='text/csv')


# ----------------------------------------------------------------------------------------------------------------

@quest_fatwas.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@quest_fatwas.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@quest_fatwas.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)
