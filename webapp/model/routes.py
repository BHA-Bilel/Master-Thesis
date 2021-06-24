from flask import Blueprint, url_for, redirect, render_template, flash, abort, send_file, request
from flask_login import current_user
from flask_sqlalchemy import Pagination

from webapp.model.forms import *
from webapp.model.utils import zipfolder, upload_model_file, get_models_summary
from flask_babel import _

from webapp.scheduled_tasks import sched, check_sim_models, check_cl_model
from webapp.utils import login_required, get_locale

model = Blueprint('model', __name__, url_prefix='/<lang_code>/model')


@model.route('/summary', methods=['GET', 'POST'])
@login_required(roles=['ME'])
def summary():
    page = request.args.get('page', 1, type=int)
    cls_dicts, sim_dicts, max_pagination = get_models_summary(page=page)

    return render_template('models/summary.html', cls_dicts=cls_dicts, sim_dicts=sim_dicts, max_pagination=max_pagination)


@model.route('/download/')  # sending file is a get not a post
@login_required(roles=['ME'])
def download():
    if not current_user.is_admin():
        abort(403)
    memory_file = zipfolder()
    return send_file(memory_file, attachment_filename='models.zip', mimetype='application/zip', as_attachment=True)


@model.route('/maintenance', methods=['get', 'post'])
@login_required(roles=['ME'])
def maintenance():
    uploadModelsForm = UploadModelsForm(meta={'locales': get_locale()})
    trainForm = TrainForm(meta={'locales': get_locale()})

    if uploadModelsForm.upload_models.data and uploadModelsForm.validate_on_submit():
        sched.add_job(upload_model_file, args=[uploadModelsForm.file])
        flash(_('Models are being uploaded in the background'), 'success')
    elif trainForm.download.data and trainForm.validate_on_submit():
        return redirect(url_for('administration.download', lang_code='en'))
    elif trainForm.train_cl.data and trainForm.validate_on_submit():
        sched.add_job(check_cl_model)
        flash(_('Checking for possible classification model training in the background'), 'success')
    elif trainForm.train_sim.data and trainForm.validate_on_submit():
        sched.add_job(check_sim_models)
        flash(_('Checking for possible similarity models training in the background'), 'success')

    return render_template('models/maintenance.html', uploadModelsForm=uploadModelsForm, trainForm=trainForm)
