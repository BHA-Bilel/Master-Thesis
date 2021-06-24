from csv import DictWriter
from io import StringIO

from webapp.models import Fatwa, FatwaClass, DelFatwa


def get_all_fatwas(mufti_id=None, name='all', page=1):
    if name == 'all':
        if mufti_id:
            fatwas = Fatwa.query.filter_by(mufti_id=mufti_id).order_by(Fatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
        else:
            fatwas = Fatwa.query.order_by(Fatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        if mufti_id:
            fatwas = Fatwa.query.filter_by(mufti_id=mufti_id, class_id=cl.id).order_by(Fatwa.id.desc()).paginate(per_page=20, page=page,
                                                                                                                 error_out=True)
        else:
            fatwas = Fatwa.query.filter_by(class_id=cl.id).order_by(Fatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    return fatwas


def count_all_fatwas(mufti_id=None, name=None):
    if name == 'all':
        if mufti_id:
            count = Fatwa.query.filter_by(mufti_id=mufti_id).count()
        else:
            count = Fatwa.query.count()
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        if mufti_id:
            count = Fatwa.query.filter_by(mufti_id=mufti_id, cl_id=cl.id).count()
        else:
            count = Fatwa.query.filter_by(cl_id=cl.id).count()
    return count


def count_del_fatwas(mufti_id=None):
    if mufti_id:
        count = DelFatwa.query.filter_by(mufti_id=mufti_id).count()
    else:
        count = DelFatwa.query.count()
    return count


def get_del_fatwas(page, mufti_id=None):
    if mufti_id:
        questions = DelFatwa.query.filter_by(mufti_id=mufti_id).order_by(DelFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    else:
        questions = DelFatwa.query.order_by(DelFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)
    return questions


def get_fatwa_summary():
    all_classes = FatwaClass.query.all()
    summary = dict()
    for row in all_classes:
        summary[row.name] = Fatwa.query.filter_by(class_id=row.id).count()
    return summary


def backup_fatwas_csv(cl):
    new_csvfile = StringIO()
    new_csvfile.name = 'fatwas_export-' + cl.name
    columns = ['mufti_id', 'topic', 'question', 'answer']
    writer = DictWriter(new_csvfile, fieldnames=columns)
    writer.writeheader()
    dataset = get_export_fatwas(cl.id)
    for data in dataset:
        writer.writerow({'mufti_id': data.mufti_id, 'topic': cl.name, 'question': data.question, 'answer': data.answer})
    new_csvfile.seek(0)
    return new_csvfile


def get_export_fatwas(cl_id):
    return Fatwa.query.with_entities(Fatwa.mufti_id, Fatwa.question, Fatwa.answer).filter_by(class_id=cl_id).all()
