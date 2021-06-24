import zipfile
from io import BytesIO

from flask import current_app
import os

from flask_sqlalchemy import Pagination

from webapp import FatwaClass
from webapp.models import ClTrain, ClAnnex, SimAnnex


def get_models_summary(page):
    cl_trains = ClTrain.query.order_by(ClTrain.id.desc()).paginate(per_page=20, page=page, error_out=False)
    cl_annexes = ClAnnex.query.all()
    sim_annexes = SimAnnex.query.order_by(SimAnnex.id.desc()).paginate(per_page=20, page=page, error_out=False)
    all_classes = FatwaClass.query.all()
    id_to_name = dict()
    for cl in all_classes:
        id_to_name[cl.id] = cl.name
    cls_dicts = []
    for cl_train in cl_trains:
        cl_dicts = []
        for cl_annex in cl_annexes:
            if cl_annex.train_id == cl_train.id:
                cl_dicts.append({
                    'fatwa_class': id_to_name[cl_annex.class_id],
                    'precision': cl_annex.precision,
                    'recall': cl_annex.recall,
                    'f1-score': cl_annex.f1_score
                })
        cls_dicts.append({
            'date': cl_train.learning_date,
            'data_per_class': cl_train.data_per_class,
            'accuracy': cl_train.accuracy,
            'annexes': cl_dicts
        })
    sim_dicts = []
    for sim_train in sim_annexes:
        sim_dicts.append({'date': sim_train.learning_date,
                          'data_number': sim_train.data_number,
                          'fatwa_class': id_to_name[sim_train.class_id],
                          'fatwas': sim_train.data_number - sim_train.last_vol_id,
                          'vol_fatwas': sim_train.last_vol_id,
                          'quest_fatwas': sim_train.data_number - sim_train.first_quest_id
                          })
    if cl_trains.total > sim_annexes.total:
        max_pagination = cl_trains
    else:
        max_pagination = sim_annexes
    return cls_dicts, sim_dicts, max_pagination


def upload_model_file(file):
    # if filename = models extract to models folder
    # if filename = scikit_class extract to classification folder
    # if filename > 0 extract to sim folder /filename
    if file.name == 'models':
        extract_path = current_app.config['MODELS_PATH']
    else:
        extract_path = current_app.config['MODELS_PATH'] + "/" + file.name

    save_path = os.path.join(current_app.config['MODELS_PATH'], 'temp.zip')
    file.data.save(save_path)
    with zipfile.ZipFile(save_path, 'r') as zipObj:
        zipObj.extractall(extract_path)
    os.remove(save_path)


def zipfolder(fatwa_class=-1):
    # if fatwa_class = -1 zip all models
    # if fatwa_class = 0 zip classification folder
    # if fatwa_class > 0 zip sim folder
    if fatwa_class == -1:
        path = current_app.config['MODELS_PATH']
    elif fatwa_class == 0:
        path = current_app.config['MODELS_PATH'] + "/scikit_class/"
    else:
        path = current_app.config['MODELS_PATH'] + "/" + fatwa_class
    rootlen = len(path) + 1
    data = BytesIO()
    with zipfile.ZipFile(data, 'w', zipfile.ZIP_DEFLATED) as zipobj:
        for base, dirs, files in os.walk(path):
            for file in files:
                fn = os.path.join(base, file)
                zipobj.write(fn, fn[rootlen:])
    data.seek(0)
    return data
