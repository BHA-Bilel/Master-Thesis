from csv import DictWriter
from io import StringIO

from webapp.models import VolFatwa, FatwaClass, DelVolFatwa

from urllib.parse import urlparse


def get_domain(link):
    return urlparse(link).netloc


def count_vol_fatwas(fatwa_class=None, user_id=None, class_id=None):
    if user_id and fatwa_class:
        fat_cl = FatwaClass.query.filter_by(name=fatwa_class).first()
        return VolFatwa.query.filter(VolFatwa.user_id == user_id, VolFatwa.class_id == fat_cl.id).count()
    elif user_id:
        return VolFatwa.query.filter(VolFatwa.user_id == user_id).count()
    elif fatwa_class:
        fat_cl = FatwaClass.query.filter_by(name=fatwa_class).first()
        return VolFatwa.query.filter(VolFatwa.class_id == fat_cl.id).count()
    elif class_id:
        return VolFatwa.query.filter_by(class_id=class_id).count()
    else:
        all_classes = FatwaClass.query.all()
        vol_fataws = dict()
        for row in all_classes:
            vol_fataws[row.name] = VolFatwa.query.filter(VolFatwa.class_id == row.id).count()
        return vol_fataws


def get_all_vol_fatwas(name, page):
    if name == 'all':
        fatwas = VolFatwa.query.order_by(VolFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        fatwas = VolFatwa.query.filter_by(class_id=cl.id).order_by(VolFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    return fatwas


def count_all_vol_fatwas(name):
    if name == 'all':
        fatwas = VolFatwa.query.count()
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        fatwas = VolFatwa.query.filter_by(class_id=cl.id).count()
    return fatwas


def count_user_vol_fatwas(user_id, name):
    if name == 'all':
        fatwas = VolFatwa.query.filter_by(user_id=user_id).count()
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        fatwas = VolFatwa.query.filter_by(user_id=user_id, class_id=cl.id).count()
    return fatwas


def get_user_vol_fatwas(user_id, name, page):
    if name == 'all':
        fatwas = VolFatwa.query.filter_by(user_id=user_id).order_by(VolFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        fatwas = VolFatwa.query.filter_by(user_id=user_id, class_id=cl.id).order_by(VolFatwa.id.desc()).paginate(per_page=20, page=page,
                                                                                                                 error_out=True)
    return fatwas


def count_del_vol_fatwas(user_id=None):
    if user_id:
        count = DelVolFatwa.query.filter_by(user_id=user_id).count()
    else:
        count = DelVolFatwa.query.count()
    return count


def get_del_quest_fatwas(page, user_id=None):
    if user_id:
        questions = DelVolFatwa.query.filter_by(user_id=user_id).order_by(DelVolFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    else:
        questions = DelVolFatwa.query.order_by(DelVolFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    return questions


def backup_vol_fatwas_csv(cl):
    new_csvfile = StringIO()
    new_csvfile.name = 'vol_fatwas_export-' + cl.name
    columns = ['user_id', 'topic', 'question', 'answer']
    writer = DictWriter(new_csvfile, fieldnames=columns)
    writer.writeheader()
    dataset = get_export_quest_fatwas(cl.id)
    for data in dataset:
        writer.writerow({'user_id': data.user_id, 'topic': cl.name, 'question': data.question, 'answer': data.answer})
    new_csvfile.seek(0)
    return new_csvfile


def get_export_quest_fatwas(cl_id):
    return VolFatwa.query.with_entities(VolFatwa.mufti_id, VolFatwa.question, VolFatwa.answer).filter_by(class_id=cl_id).all()
