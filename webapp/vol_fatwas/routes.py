from flask import Blueprint, url_for, render_template, flash, request, redirect, abort, g, current_app, session, Response
from flask_login import current_user

from webapp import User, db, FatwaClass
from webapp.models import VolFatwa, Website, DelVolFatwa
from webapp.utils import login_required, get_locale, translate
from webapp.vol_fatwas.forms import VolFatwaForm
from webapp.vol_fatwas.utils import count_all_vol_fatwas, get_all_vol_fatwas, get_domain, backup_vol_fatwas_csv, count_user_vol_fatwas, \
    get_user_vol_fatwas, count_del_vol_fatwas, get_del_vol_fatwas
from flask_babel import _

from webapp.websites.utils import zipfiles

vol_fatwas = Blueprint('vol_fatwas', __name__, url_prefix='/<lang_code>/vol_fatwas')


@vol_fatwas.route('/<string:name>', methods=['GET', 'POST'])
def all_vol_fatwas(name='all'):
    page = request.args.get('page', 1, type=int)
    total = count_all_vol_fatwas(name=name)
    if not total:
        abort(404)
    fatwas = get_all_vol_fatwas(name=name, page=page)
    usernames = dict()
    websites = dict()
    for fatwa in fatwas.items:
        if fatwa.user_id not in usernames:
            mufti = User.query.get(fatwa.mufti_id)
            usernames[fatwa.mufti_id] = mufti.username
        if fatwa.website_id not in websites:
            website = Website.query.get(fatwa.website_id)
            websites[fatwa.website_id] = website.id
    return render_template('vol_fatwas/all_vol_fatwas.html', title=_('fatwas'), fatwas=fatwas, name=name, route='all_vol_fatwas',
                           translated_name=translate(fatwa_class=name), total=total, usernames=usernames, websites=websites)


@vol_fatwas.route('/<string:name>/deleted', methods=['GET', 'POST'])
@login_required(roles=['Admin'])
def del_vol_fatwas():
    page = request.args.get('page', 1, type=int)
    total = count_del_vol_fatwas()
    if not total:
        abort(404)
    fatwas = get_del_vol_fatwas(page=page)
    usernames = dict()
    for fatwa in fatwas.items:
        if fatwa.deleter_id not in usernames:
            deleter = User.query.get(fatwa.deleter_id)
            usernames[fatwa.deleter_id] = deleter.username
        if fatwa.user_id not in usernames:
            user = User.query.get(fatwa.user_id)
            usernames[fatwa.user_id] = user.id
    return render_template('vol_fatwas/del_vol_fatwas.html', title=_('deleted fatwas'), fatwas=fatwas, route='del_vol_fatwas',
                           total=total, usernames=usernames)


@vol_fatwas.route('/<string:username>/<string:name>', methods=['GET', 'POST'])
def user_vol_fatwas(username, name='all'):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    total = count_user_vol_fatwas(user_id=user.id, name=name)
    if not total:
        abort(404)
    fatwas = get_user_vol_fatwas(user_id=user.id, name=name, page=page)
    websites = dict()
    for fatwa in fatwas.items:
        if fatwa.website_id not in websites:
            website = Website.query.get(fatwa.website_id)
            websites[fatwa.website_id] = website.id
    return render_template('vol_fatwas/all_vol_fatwas.html', title=_('fatwas'), fatwas=fatwas, route='user_vol_fatwas',
                           username=username, name=name, total=total, websites=websites)


@vol_fatwas.route('/deleted/<string:username>', methods=['GET', 'POST'])
@login_required(roles=['Admin'])
def user_del_vol_fatwas(username):
    # show this user's deleted vol_fatwas
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    total = count_del_vol_fatwas(user_id=user.id)
    if not total:
        abort(404)
    fatwas = get_del_vol_fatwas(user_id=user.id, page=page)
    usernames = dict()
    usernames[user.id] = user.username
    for fatwa in fatwas.items:
        if fatwa.deleter_id not in usernames:
            deleter = Website.query.get(fatwa.deleter_id)
            usernames[fatwa.deleter_id] = deleter.id
    return render_template('vol_fatwas/del_vol_fatwas.html', title=_('deleted fatwas'), fatwas=fatwas,
                           usernames=usernames, total=total, route='user_del_vol_fatwas')


@vol_fatwas.route('/add', methods=['GET', 'POST'])
@login_required(roles=['User'])
def add_vol_fatwa():
    if current_user.ban_vol:
        flash(_('Unfortunately, you are banned from volunteering fatwas'), 'warning')
        return redirect(url_for('main.home'))

    if not current_user.ver_em:
        flash(_('You need to verify your email in order to volunteer fatwas!'), 'warning')
        return redirect(url_for('main.home'))

    form = VolFatwaForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        website = Website.query.filter_by(domain=get_domain(form.link.data)).first()
        fatwa = VolFatwa(question=form.question.data, answer=form.answer.data, class_id=form.fatwa_class.id,
                         user_id=current_user.id, link=form.link.data, website_id=website.id)
        db.session.add(fatwa)
        db.session.commit()
        flash(_('Thank you for volunteering this fatwa'), 'success')
        return redirect(url_for('vol_fatwas.vol_fatwa', id=vol_fatwa.id))
    flash(_('Please consider checking similar fatwas before adding a new one'), 'info')
    return render_template('vol_fatwas/change.html', title=_('new voluntary fatwa'), form=form, legend=_('New voluntary fatwa'))


@vol_fatwas.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required(roles=['Mufti', 'User'])
def edit_vol_fatwa(id):
    fatwa = VolFatwa.query.get_or_404(id)

    if current_user.id != fatwa.user_id:
        abort(403)

    if not current_user.ver_em:
        flash(_('You need to verify your email in order to edit this fatwa!'), 'warning')
        return redirect(url_for('vol_fatwas.vol_fatwa', id=id))

    if session['role'] == 'User' and current_user.ban_vol:
        flash(_('Unfortunately, you no longer have any control of your fatwas'), 'warning')
        return redirect(url_for('vol_fatwas.vol_fatwa', id=id))

    form = VolFatwaForm()
    if form.validate_on_submit():
        fatwa.question = form.question.data
        fatwa.answer = form.answer.data
        fatwa.class_id = form.fatwa_class.id
        if form.link.data != fatwa.link:
            website = Website.query.filter_by(domain=get_domain(form.link.data)).first()
            fatwa.link = form.link.data
            fatwa.website_id = website.id
        db.session.commit()
        flash(_('Fatwa has been updated!'), 'success')
        return redirect(url_for('vol_fatwas.vol_fatwa', id=vol_fatwa.id))
    elif request.method == 'GET':
        form.fatwa_class.id = fatwa.class_id
        form.question.data = fatwa.question
        form.answer.data = fatwa.answer
        form.link.data = fatwa.link
    return render_template('vol_fatwas/change.html', title=_('edit voluntary fatwa'), form=form, legend=_('Edit voluntary fatwa'))


@vol_fatwas.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_vol_fatwa(id):
    fatwa = VolFatwa.query.get_or_404(id)

    if session['role'] == 'User' and current_user.id != fatwa.user_id:
        abort(403)

    if not current_user.ver_em:
        flash(_('You need to verify your email in order to delete this fatwa!'), 'warning')
        return redirect(url_for('vol_fatwas.vol_fatwa', id=id))

    if current_user.id == fatwa.user_id and current_user.ban_vol:
        flash(_('Unfortunately, you no longer have any control of your fatwas'), 'warning')
        return redirect(url_for('vol_fatwas.vol_fatwa', id=id))

    if (session['role'] == 'Admin' or session['role'] == 'Mufti') and fatwa.user_id != current_user.id:
        del_fatwa = DelVolFatwa(question=fatwa.question, answer=fatwa.answer, link=fatwa.link,
                                user_id=fatwa.user_id, deleter_id=current_user.id)
        db.session.add(del_fatwa)
    db.session.delete(fatwa)
    db.session.commit()
    flash(_('Fatwa has been deleted!'), 'success')
    return redirect(url_for('main.home'))


@vol_fatwas.route('/<int:id>')
def vol_fatwa(id):
    fatwa = VolFatwa.query.get_or_404(id)
    user = User.query.with_entities(User.username).filter_by(id=fatwa.user_id).first()
    return render_template('vol_fatwas/vol_fatwa.html', title=_('fatwa'), fatwa=fatwa, username=user.username)


@vol_fatwas.route('/<string:name>/download', methods=['POST'])
@login_required(roles=['ME'])
def download_vol_fatwas(name='all'):
    if name == 'all':
        files = []
        all_classes = FatwaClass.query.all()
        for cl in all_classes:
            files.append(backup_vol_fatwas_csv(cl=cl))
        file = zipfiles(files=files)
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            abort(404)
        file = backup_vol_fatwas_csv(cl=cl)
    flash(_('Corpus exported to your machine'), 'success')
    return Response(file, mimetype='text/csv')


# ------------------------------------------------------------------------------------------------------------------


@vol_fatwas.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@vol_fatwas.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@vol_fatwas.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)
