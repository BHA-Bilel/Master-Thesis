import csv
from io import TextIOWrapper

from flask import Blueprint, url_for, render_template, flash, request, redirect, abort, g, current_app, Response

from webapp import db, User
from webapp.websites.utils import get_fatwas, get_download_websites, zipfiles, get_websites_summary, count_taken_fatwas, count_websites
from webapp.utils import login_required, get_locale
from webapp.websites.utils import get_websites
from webapp.scheduled_tasks import sched
from webapp.websites.utils import upload_websites_fatwas, export_websites_fatwas
from webapp.websites.forms import *
from flask_login import current_user
from flask_babel import _

websites = Blueprint('websites', __name__, url_prefix='/<lang_code>/websites')


@websites.route('/', methods=['GET', 'POST'])
def all_websites():
    page = request.args.get('page', 1, type=int)
    summmary, websites = get_websites_summary(page=page)
    total = count_websites()
    users = User.query.with_entities(User.id, User.username).all()
    usernames = dict()
    for user in users:
        usernames[user.id] = user.username
    return render_template('websites/all_websites.html', title=_('trusted websites'),
                           total=total,
                           websites=websites, summmary=summmary, usernames=usernames)


@websites.route('/<int:id>')
def website(id):
    page = request.args.get('page', 1, type=int)
    website = Website.query.with_entities(Website.taken_fatwas).filter_by(id=id).all()
    taken_fatwas = get_fatwas(page=page, website=website)
    total = count_taken_fatwas(website_id=website.id)
    return render_template('websites/website.html', title=_('voluntary fatwa'), website=website,
                           taken_fatwas=taken_fatwas, total=total)


@websites.route('/add', methods=['GET', 'POST'])
@login_required(roles=['ME', 'Mufti'])
def add_website():
    if not current_user.ver_em:
        flash(_('You need to verify your email in order to add new voluntary fatwas!'), 'warning')
        return redirect(url_for('main.home'))
    form = WebsiteForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        website = Website(domain=form.domain.data, description=form.description.data)
        db.session.add(website)
        db.session.commit()
        flash(_('Website added successfully'), 'success')
        return redirect(url_for('websites.website', id=website.id))

    flash(_('Please consider checking similar fatwas before adding new ones'), 'info')
    return render_template('websites/change.html', title=_('new fatwa'), form=form, legend=_('New fatwa'))


@websites.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required(roles=['ME', 'Mufti'])
def edit_website(id):
    website = Website.query.get_or_404(id)

    if not current_user.ver_em:
        flash(_('You need to verify your email in order to edit this website!'), 'warning')
        return redirect(url_for('websites.website', id=id))

    form = WebsiteForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        website.domain = form.domain.data
        website.description = form.description.data
        db.session.commit()
        flash(_('Website updated successfully!'), 'success')
        return redirect(url_for('websites.website', id=website.id))
    elif request.method == 'GET':
        form.domain.data = website.domain
        form.description.data = website.description
    return render_template('websites/change.html', title=_('edit fatwa'), website=website, form=form, legend=_('Edit fatwa'))


@websites.route('/<int:id>/delete', methods=['POST'])
@login_required(roles=['ME', 'Mufti'])
def delete_website(id):
    website = Website.query.get_or_404(id)

    if not current_user.ver_em:
        flash(_('You need to verify your email in order to delete this website!'), 'warning')
        return redirect(url_for('websites.website', id=id))

    db.session.delete(website)
    db.session.commit()
    flash(_('Website has been deleted!'), 'success')
    return redirect(url_for('websites.all_websites'))


@websites.route('/<int:id>/download', methods=['POST'])
@login_required(roles=['ME'])
def download_websites_fatwas(id=0):
    if id == 0:
        websites = get_download_websites()
        files = []
        for website in websites:
            files.append(export_websites_fatwas(domain=website.domain, taken_fatwas=website.taken_fatwas))
        file = zipfiles(files)
    else:
        website = get_download_websites(website_id=id)
        if not website:
            abort(404)
        file = export_websites_fatwas(domain=website.domain, taken_fatwas=website.taken_fatwas)
    flash(_('Corpus exported to your machine'), 'success')
    return Response(file, mimetype='text/csv')


@websites.route('/upload', methods=['get', 'post'])
@login_required(roles=['ME'])
def upload():
    # todo change after uploading fatwas 1224
    uploadCorpForm = UploadCorpForm(meta={'locales': get_locale()})
    if uploadCorpForm.validate_on_submit():
        COLUMNS = ['topic', 'question', 'answer']  # 'webiste_id'
        csv_file = TextIOWrapper(uploadCorpForm.file.data, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = next(csv_reader)
        good = True
        for col in COLUMNS:
            if col not in header:
                flash(_('csv header should contain: [topic, question, answer] tuples in this order!'), 'warning')
                good = False
        if not next(csv_reader):
            flash(_('Empty csv file!'), 'warning')
            good = False
        if good:
            sched.add_job(upload_websites_fatwas, args=[uploadCorpForm.domain.id, csv_file, csv_reader])
            flash(_('Corpus is being uploaded in the background'), 'success')

    return render_template('websites/upload_corp.html', uploadCorpForm=uploadCorpForm)


# --------------------------------------------------------------------------------------------------


@websites.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@websites.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@websites.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)
