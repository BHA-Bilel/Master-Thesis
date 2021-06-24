from flask import Blueprint, session, url_for, render_template, redirect, current_app, abort, flash, g, request, Markup

from webapp import ctx
from webapp.models import User, VolFatwa, QuestFatwa, Fatwa, SimAnnex
from webapp.qasystem.forms import *
from webapp.model.scikit_class import predict_class

import bisect

from webapp.model.doc2vec_sim import get_sim
from webapp.model.preprocess_docs import pre_process
from webapp.model.lsi_sim import get_sims
from webapp.qasystem.serialize import Data
from webapp.qasystem.utils import inverse
from flask_babel import _

from webapp.utils import translate, get_locale

qasystem = Blueprint('qasystem', __name__, url_prefix='/<lang_code>/qasystem')


@qasystem.route('/', methods=['GET', 'POST'])
def query():
    form = QueryForm(meta={'locales': get_locale()})
    if form.validate_on_submit():
        session['question'] = form.fatwa.data
        return redirect(url_for('qasystem.result', _method="GET"))
    return render_template('qasystem/query.html', form=form, title='Query input')


@qasystem.route('/classification', methods=['GET', 'POST'])
def classification():
    if session['question']:
        question = session['question']
        session['fatwa_class'] = predict_class(pre_process(question))
        flash(_('QuestFatwa is classified as %(fatwa_class)s', fatwa_class=translate(fatwa_class=session["fatwa_class"])), 'success')
        form = ClassForm(meta={'locales': get_locale()})
        if form.validate_on_submit():
            if form.fatwa_class.data != '':
                session['fatwa_class'] = form.fatwa_class.data
            return redirect(url_for('qasystem.results'))
        else:
            return render_template('qasystem/classification.html', question=question, form=form, title=_('classification'))

    else:
        flash(_('You should enter a query first !'), 'warning')
        return redirect(url_for('qasystem.query'))


@qasystem.route("/results")
def results():
    if not session['question']:
        flash(_('You should enter a query first !'), 'warning')
        return redirect(url_for('qasystem.query'))

    with ctx:
        question = session['question']
        fatwa_class = session['fatwa_class']
        cl = FatwaClass.query.filter_by(name=fatwa_class).first()
        tokenized_doc = pre_process(question)
        doc2vec_sim = get_sim(cl_id=cl.id, tokenized_doc=tokenized_doc)
        lsi_sim = get_sims(cl_id=cl.id, tokenized_doc=tokenized_doc)

    annex = SimAnnex.query.order_by(SimAnnex.id.desc()).first()
    last_vol_id = annex.last_vol_id
    first_quest_id = annex.first_quest_id

    document_order = 1
    result = []
    fatwas = []
    min_sim = current_app.config['MIN_QASYSTEM_SIM']
    max_order = current_app.config['MAX_DOC_ORDER']
    x = 0
    y = 0
    doc2vec_sim
    lsi_sim
    while x < max_order and y < max_order:
        a = doc2vec_sim[x][1] < min_sim
        b = lsi_sim[y][1] < min_sim
        if a or b:
            break
        if doc2vec_sim[x][1] > lsi_sim[y][1]:
            doc_id = doc2vec_sim[x][0] + 1
            sim = doc2vec_sim[x][1]
            x += 1
        else:
            doc_id = lsi_sim[y][0] + 1
            sim = lsi_sim[y][1]
            y += 1

        if doc_id <= last_vol_id:
            fatwa = VolFatwa.query.filter_by(id=doc_id).first()
        elif doc_id >= first_quest_id > 0:
            fatwa = QuestFatwa.query.filter_by(id=doc_id - first_quest_id).first()
        else:
            fatwa = Fatwa.query.filter_by(id=doc_id - last_vol_id).first()
        if fatwa:
            result = Data(model='DOC2VEC', similarity=str(sim), doc_id=doc_id)
            if result not in results:
                fatwas.append(fatwa)
                results.append(result)
            else:
                for j in range(len(results)):
                    if results[j] == result:
                        results[j].add_model(result.model, result.similarity)
                        break

    while x < 5:
        while x < max_order and y < max_order:
            if doc2vec_sim[x][1] < min_sim:
                break
            doc_id = doc2vec_sim[x][0] + 1
            sim = doc2vec_sim[x][1]
            x += 1
            if doc_id <= last_vol_id:
                fatwa = VolFatwa.query.filter_by(id=doc_id).first()
            elif doc_id >= first_quest_id > 0:
                fatwa = QuestFatwa.query.filter_by(id=doc_id - first_quest_id).first()
            else:
                fatwa = Fatwa.query.filter_by(id=doc_id - last_vol_id).first()
            if fatwa:
                result = Data(model='DOC2VEC', similarity=str(sim), doc_id=doc_id)
                if result not in results:
                    fatwas.append(fatwa)
                    results.append(result)
                else:
                    for j in range(len(results)):
                        if results[j] == result:
                            results[j].add_model(result.model, result.similarity)
                            break
    while y < 5:
        while x < max_order and y < max_order:
            if lsi_sim[y][1] < min_sim:
                break
            doc_id = lsi_sim[y][0] + 1
            sim = lsi_sim[y][1]
            y += 1
            if doc_id <= last_vol_id:
                fatwa = VolFatwa.query.filter_by(id=doc_id).first()
            elif doc_id >= first_quest_id > 0:
                fatwa = QuestFatwa.query.filter_by(id=doc_id - first_quest_id).first()
            else:
                fatwa = Fatwa.query.filter_by(id=doc_id - last_vol_id).first()
            if fatwa:
                result = Data(model='DOC2VEC', similarity=str(sim), doc_id=doc_id)
                if result not in results:
                    fatwas.append(fatwa)
                    results.append(result)
                else:
                    for j in range(len(results)):
                        if results[j] == result:
                            results[j].add_model(result.model, result.similarity)
                            break
    if not fatwas:
        flash(_('You can ask this question') + Markup(
            f' <a href={url_for("quest_fatwas.add_quest_fatwa", question=question)} class="alert-link">' + _(
                'Here') + '</a>'), 'info')
        return redirect(url_for('qasystem.error', question=session['question']))
    else:
        usernames = dict()
        for fatwa in fatwas:
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

        return render_template('qasystem/results.html', fatwas=fatwas, results=results, question=question,
                               title=_('results'), fatwa_class=fatwa_class, usernames=usernames)


@qasystem.route("/error")
def error():
    message = _('The models did not find any similar questions to yours, please consider asking the question' + Markup(
        f' <a href={url_for("quest_fatwas.add_quest_fatwa", fatwa_class=session["fatwa_class"], question=session["fatwa"])} class ="alert-link" > ' + _(
            'Here') + '</a>'))
    return render_template('qasystem/error.html', message=message)


# ------------------------------------------------------------------------------------------
@qasystem.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@qasystem.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@qasystem.before_request
def before_request():
    if current_app.config['MODELS_TRAINING']:
        return render_template('qasystem/error.html', message=_('The models are currently training, they will be available in few minutes.'))
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)
