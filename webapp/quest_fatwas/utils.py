from csv import DictWriter
from io import StringIO

from webapp.models import QuestFatwa, FatwaClass, DelQuestion


def get_all_quest_fatwas(name, page, answered):
    if name == 'all':
        quest_fatwas = QuestFatwa.query.filter(QuestFatwa.mufti_id != None if answered else QuestFatwa.mufti_id == None).order_by(
            QuestFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        quest_fatwas = QuestFatwa.query.filter(QuestFatwa.class_id == cl.id,
                                               QuestFatwa.mufti_id != None if answered else QuestFatwa.mufti_id == None).order_by(
            QuestFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    return quest_fatwas


def count_all_quest_fatwas(name, answered):
    if name == 'all':
        count = QuestFatwa.query.filter(QuestFatwa.mufti_id != None if answered else QuestFatwa.mufti_id == None).count()
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        count = QuestFatwa.query.filter(QuestFatwa.cl_id == cl.id, QuestFatwa.mufti_id != None if answered else QuestFatwa.mufti_id == None).count()
    return count


def count_user_quest_fatwas(user_id, answered, name):
    if name == 'all':
        count = QuestFatwa.query.filter(QuestFatwa.user_id == user_id,
                                        QuestFatwa.mufti_id != None if answered else QuestFatwa.mufti_id == None).count()
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        count = QuestFatwa.query.filter(QuestFatwa.user_id == user_id, QuestFatwa.cl_id == cl.id,
                                        QuestFatwa.mufti_id != None if answered else QuestFatwa.mufti_id == None).count()
    return count


def get_user_quest_fatwas(user_id, page, answered, name):
    if name == 'all':
        quest_fatwas = QuestFatwa.query.filter(QuestFatwa.user_id == user_id,
                                               QuestFatwa.mufti_id != None if answered
                                               else QuestFatwa.mufti_id == None).order_by(QuestFatwa.id.desc()).paginate(per_page=20, page=page,
                                                                                                                         error_out=True)
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        quest_fatwas = QuestFatwa.query.filter(QuestFatwa.user_id == user_id, QuestFatwa.class_id == cl.id,
                                               QuestFatwa.mufti_id != None if answered else QuestFatwa.mufti_id == None).order_by(
            QuestFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    return quest_fatwas


def count_del_quest_fatwas(user_id=None):
    if user_id:
        count = DelQuestion.query.filter_by(user_id=user_id).count()
    else:
        count = DelQuestion.query.count()
    return count


def get_del_quest_fatwas(page, user_id=None):
    if user_id:
        questions = DelQuestion.query.filter_by(user_id=user_id).order_by(DelQuestion.id.desc()).paginate(per_page=20, page=page, error_out=True)
    else:
        questions = DelQuestion.query.order_by(DelQuestion.id.desc()).paginate(per_page=20, page=page, error_out=True)
    return questions


def count_mufti_quest_fatwas(mufti_id, name):
    if name == 'all':
        count = QuestFatwa.query.filter_by(mufti_id=mufti_id).count()
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        count = QuestFatwa.query.filter(QuestFatwa.mufti_id == mufti_id, QuestFatwa.cl_id == cl.id).count()
    return count


def get_mufti_quest_fatwas(mufti_id, page, name):
    if name == 'all':
        quest_fatwas = QuestFatwa.query.filter_by(mufti_id=mufti_id).order_by(QuestFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        quest_fatwas = QuestFatwa.query.filter(QuestFatwa.mufti_id == mufti_id, QuestFatwa.class_id == cl.id).order_by(
            QuestFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    return quest_fatwas


def backup_quest_fatwas_csv(cl):
    new_csvfile = StringIO()
    new_csvfile.name = 'quest_fatwas_export-' + cl.name
    columns = ['mufti_id', 'topic', 'question', 'answer']
    writer = DictWriter(new_csvfile, fieldnames=columns)
    writer.writeheader()
    dataset = get_export_quest_fatwas(cl.id)
    for data in dataset:
        writer.writerow({'mufti_id': data.mufti_id, 'topic': cl.name, 'question': data.question, 'answer': data.answer})
    new_csvfile.seek(0)
    return new_csvfile


def get_export_quest_fatwas(cl_id):
    return QuestFatwa.query.with_entities(QuestFatwa.mufti_id, QuestFatwa.question, QuestFatwa.answer).filter_by(class_id=cl_id).all()
