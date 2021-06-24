from flask import Blueprint, url_for, redirect, g, current_app, abort, request, Response, flash, render_template
from flask_login import current_user
from flask_sqlalchemy import Pagination

from webapp import FatwaClass, db, User
from webapp.fatwa_class.forms import FatwaClassForm
from webapp.fatwa_class.utils import export_all_fatwas_csv, get_all_fatwas, get_classes_summary, count_all_fatwas
from webapp.utils import login_required, get_locale
from flask_babel import _

from webapp.websites.utils import zipfiles

fatwa_class = Blueprint('fatwa_class', __name__, url_prefix='/<lang_code>')


@fatwa_class.route('/new', methods=['GET', 'POST'])
@login_required(roles=['Admin', 'Mufti'])
def new_fatwa_class():
    if not current_user.ver_em:
        flash(_('You need to verify your email in order to add new fatwa classes!'), 'warning')
        return redirect(url_for('main.home'))
    form = FatwaClassForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        fatwa_class = FatwaClass(form.name.name)
        db.session.add(fatwa_class)
        db.session.commit()
        flash(_('Fatwa class added successfully'), 'success')
        return redirect(url_for('fatwa_class.fatwa_class', name=fatwa_class.name))
    return render_template('fatwa_class/change.html', title=_('new fatwa class'), form=form, legend=_('New fatwa class'))


@fatwa_class.route('/<string:name>/edit', methods=['GET', 'POST'])
@login_required(roles=['Admin', 'Mufti'])
def edit_fatwa_class(name):
    if name == 'all':
        abort(404)
    if not current_user.ver_em:
        flash(_('You need to verify your email in order to add new fatwa classes!'), 'warning')
        return redirect(url_for('main.home'))
    fatwa_class = FatwaClass.query.filter_by(name=name).first()
    if not fatwa_class:
        abort(404)
    form = FatwaClassForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        fatwa_class.name = form.name.data
        fatwa_class.description = form.description.data
        db.session.commit()
        flash(_('Fatwa class has been updated!'), 'success')
        return redirect(url_for('fatwa_class.fatwa_class', name=fatwa_class.name))
    elif request.method == 'GET':
        form.name.data = fatwa_class.name
        form.description.data = fatwa_class.description
    return render_template('fatwa_class/change.html', title=_('edit fatwa class'), form=form, legend=_('Edit fatwa class'))


@fatwa_class.route('/<string:name>/delete', methods=['POST'])
@login_required(roles=['Admin'])
def delete_fatwa_class(name):
    fatwa_class = FatwaClass.query.filter_by(name=name).first()
    if not fatwa_class:
        abort(404)

    if not current_user.ver_em:
        flash(_('You need to verify your email in order to delete this fatwa class!'), 'warning')
        return redirect(url_for('fatwa_class.fatw_class', name=name))

    db.session.delete(fatwa_class)
    db.session.commit()
    flash(_('Fatwa class has been deleted!'), 'success')
    return redirect(url_for('main.home'))


@fatwa_class.route('/<string:name>', methods=['GET', 'POST'])
def fatwa_class(name='all'):
    page = request.args.get('page', 1, type=int)
    total = count_all_fatwas(name=name)
    if not total:
        abort(404)
    usernames = dict()
    if name == 'all':
        all_classes = FatwaClass.query.all()
        fatwas = []
        max_pagination = Pagination(query=None, page=1, per_page=1, total=0, items=[])
        for cl in all_classes:
            data, pagination = get_all_fatwas(cl_id=cl.id, page=page, per_page=5)
            fatwas.extend(data)
            if pagination.total > max_pagination.total:
                max_pagination = pagination
    else:
        fatwas, max_pagination = get_all_fatwas(cl_id=cl.id, page=page, per_page=10)

    for fatwa in fatwas.items:
        if fatwa.__tablename__ == 'fatwas':
            if fatwa.mufti_id not in usernames:
                mufti = User.query.get(fatwa.mufti_id)
                usernames[fatwa.mufti_id] = mufti.username
        elif fatwa.__tablename__ == 'vol_fatwas':
            if fatwa.user_id not in usernames:
                user = User.query.get(fatwa.user_id)
                usernames[fatwa.user_id] = user.username
        elif fatwa.__tablename__ == 'quest_fatwas':
            if fatwa.mufti_id not in usernames:
                mufti = User.query.get(fatwa.mufti_id)
                usernames[fatwa.mufti_id] = mufti.username
            if fatwa.user_id not in usernames:
                user = User.query.get(fatwa.user_id)
                usernames[fatwa.user_id] = user.username

    return render_template('fatwa_class/fatwa_class.html', fatwas=fatwas, name=name, total=total,
                           usernames=usernames, max_pagination=max_pagination)


@fatwa_class.route('/all_classes', methods=['GET', 'POST'])
def fatwa_class_summary():
    page = request.args.get('page', 1, type=int)
    summary, all_classes = get_classes_summary(page=page)
    total = FatwaClass.query.count()
    return render_template('fatwa_class/fat.html', title=_('Fatwa classes'), total=total,
                           all_classes=all_classes, summary=summary)


@fatwa_class.route('/<string:name>/export', methods=['get'])
@login_required(roles=['Admin'])
def export(name='all'):
    if name == 'all':
        files = []
        all_classes = FatwaClass.query.all()
        for cl in all_classes:
            files.append(export_all_fatwas_csv(cl=cl))
        file = zipfiles(files=files)
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            abort(404)
        file = export_all_fatwas_csv(cl=cl)
    flash(_('Corpus exported to your machine'), 'success')
    return Response(file, mimetype='text/csv')


# --------------------------------------------------------------------------------

@fatwa_class.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@fatwa_class.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@fatwa_class.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)
