from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
import yaml

from webapp import FatwaClass, db
from webapp.emails import send_cl_rep, send_sim_rep, send_quest_sum
from webapp.fatwa_class.utils import count_all_quest, count_all_fatwas
from webapp.model.doc2vec_sim import create_doc2vec_model
from webapp.model.scikit_class import create_model
from webapp.model.lsi_sim import create_lsi_model
from webapp.models import ClTrain, SimAnnex, Fatwa, VolFatwa, QuestFatwa, ClAnnex
from webapp.quest_fatwas.utils import count_active_questions
from webapp.utils import translate

from sqlalchemy.sql.expression import func


def load_config():
    with open("config.yaml", "r") as file:
        config = yaml.full_load(file)
    return config


def save_config(config):
    with open("config.yaml", "w") as file:
        yaml.dump(config, file)


def check_mufti():
    all_classes = FatwaClass.query.all()
    eligible = dict()
    for cl in all_classes:
        count = count_active_questions(class_id=cl.id)
        if count > 0:
            eligible[cl.name] = count
    if eligible:
        send_quest_sum(eligible=eligible)


def check_sim_models():
    all_classes = FatwaClass.query.all()
    eligible = []
    for cl in all_classes:
        sim_annex = SimAnnex.query.filter(SimAnnex.id.desc, SimAnnex.class_id == cl.id).first()
        if not sim_annex or count_all_fatwas(name=cl.name) > sim_annex.data_number:
            eligible.append(cl)

    for cl in eligible:
        train_sim_models(cl=cl)


def train_sim_models(cl):
    dataset, last_vol_id, first_quest_id = get_sim_dataset(cl_id=cl.id)
    create_doc2vec_model(cl_id=cl.id, dataset=dataset)
    create_lsi_model(cl_id=cl.id, dataset=dataset)
    data_number = len(dataset)
    update_sim_annex(last_vol_id=last_vol_id, first_quest_id=first_quest_id, class_id=cl.id, data=data_number)
    send_sim_rep(cl_name=cl.name, data_number=data_number)


def get_sim_dataset(cl_id):
    list = VolFatwa.query.filter_by(fat_cl=cl_id).all()
    last_vol_id = len(list)
    list.extend([Fatwa.query.filter_by(fat_cl=cl_id).all()])
    first_quest_id = len(list)
    list.extend([QuestFatwa.query.filter(QuestFatwa.answer != None, QuestFatwa.class_id == cl_id).all()])
    return list, last_vol_id, first_quest_id


def update_sim_annex(last_vol_id, first_quest_id, class_id, data):
    sim = SimAnnex(last_vol_id=last_vol_id, first_quest_id=first_quest_id, class_id=class_id, data_number=data)
    db.session.add(sim)
    db.session.commit()


def check_cl_model():
    all_classes = FatwaClass.query.all()
    config = load_config()
    eligible = dict()
    minority_class = 0
    limit = 1000000
    for cl in all_classes:
        count = count_all_quest(class_id=cl.id)
        if count >= config['min_data_per_class']:
            eligible[cl.id] = count
            if count < limit:
                limit = count
                minority_class = cl.id

    last = ClTrain.query.order_by(ClTrain.id.desc()).first()
    if not last or len(eligible) > len(last.annexes):
        dataset = get_class_dataset(eligible=eligible, limit=limit)
        train_cl_model(dataset=dataset, minority_class=minority_class, limit=limit, eligible=eligible)
    elif len(eligible) == len(last.annexes):
        train = True
        for annex in last.annexes:
            if eligible[annex.class_id] and eligible[annex.class_id] <= last.data_per_class:
                train = False
                break
        if train:
            dataset = get_class_dataset(eligible=eligible, limit=limit)
            train_cl_model(dataset=dataset, minority_class=minority_class, limit=limit, eligible=eligible)


def train_cl_model(dataset, minority_class, limit, eligible):
    classification_report, out_dict = create_model(dataset=dataset, eligible=eligible)
    update_cl_report(minority_class=minority_class, data_per_class=limit, accuracy=out_dict.get('accuracy'),
                     out_dict=out_dict, train_classes=eligible)
    send_cl_rep(classification_report=classification_report)


def update_cl_report(minority_class, data_per_class, accuracy, out_dict, train_classes):
    train = ClTrain(minority_class=minority_class, data_per_class=data_per_class, accuracy=accuracy)
    db.session.add(train)
    db.session.commit()
    all_classes = FatwaClass.query.all()
    class_to_id = dict()
    for row in all_classes:
        class_to_id[row.name] = row.id

    for train_cl in train_classes:
        row = out_dict.get(train_classes[train_cl])
        cl = ClAnnex(train_id=train.id, class_id=class_to_id[train_cl], percision=row.get('precision'),
                     recall=row.get('recall'), f1_score=row.get('f1-score'))
        db.session.add(cl)
    db.session.commit()


def get_class_dataset(eligible, limit):
    dataset = []
    for train_class in eligible:
        count = VolFatwa.query.count()
        if count <= limit:
            list = VolFatwa.query.with_entities(VolFatwa.class_id, VolFatwa.question).filter_by(class_id=train_class).all()
            count += QuestFatwa.query.count()
            if count <= limit:
                list.extend([QuestFatwa.query.with_entities(QuestFatwa.class_id, QuestFatwa.question).filter_by(class_id=train_class).all()])
                count += Fatwa.query.count()
                if count <= limit:
                    list.extend(
                        [Fatwa.query.with_entities(Fatwa.class_id, Fatwa.question).filter_by(class_id=train_class).all()])
                else:
                    list.extend(
                        [Fatwa.query.with_entities(Fatwa.class_id, Fatwa.question).filter_by(class_id=train_class).order_by(func.rand()).limit(
                            limit - count).all()])
            else:
                list.extend(
                    [QuestFatwa.query.with_entities(QuestFatwa.class_id, QuestFatwa.question).filter_by(class_id=train_class).order_by(
                        func.rand()).limit(limit - count).all()])
        else:
            list = VolFatwa.query.with_entities(VolFatwa.class_id, VolFatwa.question).filter_by(class_id=train_class).order_by(func.rand()).limit(
                limit).all()
        dataset.extend(list)
    return dataset


sched = None


def start_scheduler():
    current_app.jinja_env.globals.update(translate=translate)
    global sched
    sched = BackgroundScheduler(daemon=True)

    muf_date = datetime(year=2020, month=7, day=17, hour=7, minute=0, second=0).replace(tzinfo=timezone.utc).astimezone(tz=None)
    sched.add_job(check_mufti, 'interval', id='check_mufti', weeks=1, start_date=muf_date)

    start_date = datetime(year=2020, month=7, day=17).replace(tzinfo=timezone.utc).astimezone(tz=None)
    sched.add_job(check_sim_models, 'interval', id='check_sim_models', weeks=1, start_date=start_date)
    sched.add_job(check_cl_model, 'interval', id='check_cl_model', months=1, start_date=start_date)

    sched.start()
