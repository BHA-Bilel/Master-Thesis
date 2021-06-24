from flask import Blueprint, url_for, redirect, session, g, current_app, Response

from flask import render_template, flash, request, abort

from webapp import db
from webapp.fatwas.forms import *
from flask_login import current_user

from webapp.fatwas.utils import get_all_fatwas, backup_fatwas_csv, count_all_fatwas, count_del_fatwas, get_del_fatwas
from webapp.utils import login_required, get_locale
from webapp.models import User, Fatwa
from flask_babel import _

from webapp.websites.utils import zipfiles

fatwas = Blueprint('fatwas', __name__, url_prefix='/<lang_code>/fatwas')


@fatwas.route('/new', methods=['GET', 'POST'])
@login_required(roles=['Mufti'])
def new_fatwa():
    if not current_user.ver_em:
        flash(_('You need to verify your email in order to add new fatwas!'), 'warning')
        return redirect(url_for('main.home'))
    form = FatwaForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        fatwa = Fatwa(question=form.question.data, answer=form.answer.data, class_id=form.fatwa_class.id, mufti_id=current_user.id)
        db.session.add(fatwa)
        db.session.commit()
        flash(_('Thank you for sharing this fatwa'), 'success')
        return redirect(url_for('fatwas.fatwa', id=fatwa.id))
    flash(_('Please consider checking similar fatwas before adding a new one'), 'info')
    return render_template('fatwas/change.html', title=_('new fatwa'), form=form, legend=_('New fatwa'))


@fatwas.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required(roles=['Mufti'])
def edit_fatwa(id):
    fatwa = Fatwa.query.get_or_404(id)
    if current_user.id != fatwa.mufti_id:
        abort(403)

    if not current_user.ver_em:
        flash(_('You need to verify your email in order to edit this fatwa!'), 'warning')
        return redirect(url_for('fatwas.fatwa', id=id))

    form = FatwaForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        fatwa.question = form.question.data
        fatwa.answer = form.answer.data
        fatwa.class_id = form.fatwa_class.id
        db.session.commit()
        flash(_('Fatwa has been updated!'), 'success')
        return redirect(url_for('fatwas.fatwa', id=fatwa.id))
    elif request.method == 'GET':
        form.fatwa_class.id = fatwa.class_id
        form.question.data = fatwa.question
        form.answer.data = fatwa.answer
    return render_template('fatwas/change.html', title=_('edit fatwa'), fatwa=fatwa, form=form, legend=_('Edit fatwa'))


@fatwas.route('/<int:id>/delete', methods=['POST'])
@login_required(roles=['Admin', 'Mufti'])
def delete_fatwa(id):
    fatwa = Fatwa.query.get_or_404(id)

    if session['role'] == 'Mufti' and current_user.id != fatwa.mufti_id:
        abort(403)

    if not current_user.ver_em:
        flash(_('You need to verify your email in order to delete your fatwa!'), 'warning')
        return redirect(url_for('fatwas.fatwa', id=id))

    # if session['role'] == 'Admin' and fatwa.mufti_id != current_user.id:
    #     del_fatwa = DelFatwa(mufti_id=fatwa.mufti_id, admin_id=current_user.id, question=fatwa.question, answer=fatwa.answer)
    #     db.session.add(del_fatwa)
    db.session.delete(fatwa)
    db.session.commit()
    flash(_('Fatwa has been deleted!'), 'success')
    return redirect(url_for('main.home'))


@fatwas.route('/<int:id>', methods=['GET', 'POST'])
def fatwa(id):
    fatwa = Fatwa.query.get_or_404(id)
    mufti = User.query.with_entities(User.username).filter_by(id=fatwa.mufti_id).first()
    return render_template('fatwas/fatwa.html', title=_('fatwa'), fatwa=fatwa, username=mufti.username)


@fatwas.route('/<string:name>', methods=['GET', 'POST'])
def all_fatwas(name='all'):
    page = request.args.get('page', 1, type=int)
    total = count_all_fatwas(name=name)
    if not total:
        abort(404)
    fatwas = get_all_fatwas(name=name, page=page)
    usernames = dict()
    for fatwa in fatwas.items:
        if fatwa.mufti_id not in usernames:
            mufti = User.query.get(fatwa.mufti_id)
            usernames[fatwa.mufti_id] = mufti.username
    return render_template('fatwas/all_fatwas.html', title=_('fatwas'), fatwas=fatwas,
                           name=name, total=total, usernames=usernames, route='all_fatwas')


@fatwas.route('/<string:username>/<string:name>', methods=['GET', 'POST'])
def mufti_fatwas(username, name='all'):
    mufti = User.query.filter_by(username=username).first()
    if not mufti:
        abort(404)
    page = request.args.get('page', 1, type=int)
    total = count_all_fatwas(mufti_id=mufti.id, name=name)
    fatwas = get_all_fatwas(mufti_id=mufti.id, name=name, page=page)
    usernames = dict()
    for fatwa in fatwas.items:
        if fatwa.mufti_id not in usernames:
            mufti = User.query.get(fatwa.mufti_id)
            usernames[fatwa.mufti_id] = mufti.username
    return render_template('fatwas/all_fatwas.html', title=_('fatwas'), fatwas=fatwas,
                           name=name, total=total, usernames=usernames, route='mufti_fatwas')


@fatwas.route('/deleted/<string:username>', methods=['GET', 'POST'])
@login_required(roles=['Admin'])
def mufti_del_fatwas(username):
    mufti = User.query.filter_by(username=username).first()
    if not mufti:
        abort(404)
    page = request.args.get('page', 1, type=int)
    total = count_del_fatwas(mufti_id=mufti.id)
    fatwas = get_del_fatwas(mufti_id=mufti.id, page=page)
    usernames = dict()
    usernames[mufti.id] = mufti.username
    for fatwa in fatwas.items:
        if fatwa.admin_id not in usernames:
            admin = User.query.get(fatwa.admin_id)
            usernames[fatwa.admin_id] = admin.id
    return render_template('fatwas/del_fatwas.html', title=_('deleted fatwas'), fatwas=fatwas,
                           total=total, usernames=usernames, route='mufti_del_fatwas')


@fatwas.route('/deleted', methods=['GET', 'POST'])
@login_required(roles=['Admin'])
def del_fatwas():
    page = request.args.get('page', 1, type=int)
    total = count_del_fatwas()
    if not total:
        abort(404)
    fatwas = get_del_fatwas(page=page)
    usernames = dict()
    for fatwa in fatwas.items:
        if fatwa.mufti_id not in usernames:
            mufti = User.query.get(fatwa.mufti_id)
            usernames[fatwa.mufti_id] = mufti.username
        if fatwa.admin_id not in usernames:
            admin = User.query.get(fatwa.admin_id)
            usernames[fatwa.admin_id] = admin.id
    return render_template('fatwas/del_fatwas.html', title=_('deleted fatwas'), fatwas=fatwas,
                           total=total, usernames=usernames, route='del_fatwas')


@fatwas.route('/<string:name>/download', methods=['POST'])
@login_required(roles=['Admin'])
def download_fatwas(name='all'):
    if name == 'all':
        files = []
        all_classes = FatwaClass.query.all()
        for cl in all_classes:
            files.append(backup_fatwas_csv(cl=cl))
        file = zipfiles(files=files)
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            abort(404)
        file = backup_fatwas_csv(cl=cl)
    flash(_('Corpus exported to your machine'), 'success')
    return Response(file, mimetype='text/csv')


# ---------------------------------------------------------------------------------------------

@fatwas.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@fatwas.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@fatwas.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)
