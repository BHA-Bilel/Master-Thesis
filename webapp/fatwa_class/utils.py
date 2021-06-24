from csv import DictWriter
from io import StringIO

from webapp import FatwaClass
from webapp.models import VolFatwa, QuestFatwa, Fatwa
from webapp.utils import translate


def count_all_quest(class_id=None):
    count = VolFatwa.query.filter_by(class_id=class_id).count()
    count += QuestFatwa.query.filter_by(class_id=class_id).count()
    count += Fatwa.query.filter_by(class_id=class_id).count()
    return count


def count_all_fatwas(name='all'):
    if name == 'all':
        count = VolFatwa.query.count()
        count += QuestFatwa.query.filter(QuestFatwa.mufti_id != None).count()
        count += Fatwa.query.count()
    else:
        cl = FatwaClass.query.filter_by(name=name).first()
        if not cl:
            return None
        count = VolFatwa.query.filter_by(class_id=cl.id).count()
        count += QuestFatwa.query.filter(QuestFatwa.class_id == cl.id, QuestFatwa.answer != None).count()
        count += Fatwa.query.filter_by(class_id=cl.id).count()
    return count


def get_classes_summary(page):
    summary = []
    all_classes = FatwaClass.query.paginate(page=page, per_page=20, error_out=True)
    for cl in all_classes:
        fatwas = len(cl.fatwas) + len(cl.vol_fatwas) + len(cl.quest_fatwas.filter(QuestFatwa.answer != None))
        summary.append({
            'name': translate(fatwa_class=cl.name),
            'description': cl.description,
            'fatwas': fatwas
        })
    return summary, all_classes


def export_all_fatwas_csv(cl):
    new_csvfile = StringIO()
    new_csvfile.name = 'fatwa_class_export-' + cl.name
    columns = ['topic', 'question', 'answer']
    writer = DictWriter(new_csvfile, fieldnames=columns)
    writer.writeheader()
    dataset = get_export_fatwas(cl.id)
    for data in dataset:
        writer.writerow({'topic': cl.name, 'question': data.question, 'answer': data.answer})
    new_csvfile.seek(0)
    return new_csvfile


def get_export_fatwas(cl_id):
    data = VolFatwa.query.with_entities(VolFatwa.question, VolFatwa.answer).filter_by(class_id=cl_id).all()
    data.extend([QuestFatwa.query.with_entities(QuestFatwa.question, QuestFatwa.answer).filter(QuestFatwa.class_id == cl_id,
                                                                                               QuestFatwa.answer != None).all()])
    data.extend([Fatwa.query.with_entities(Fatwa.question, Fatwa.answer).filter_by(class_id=cl_id).all()])
    return data


def get_all_fatwas(cl_id, page, per_page):
    fatwas = []
    vol_fatwas = VolFatwa.query.with_entities(VolFatwa.class_id, VolFatwa.question, VolFatwa.answer). \
        filter_by(class_id=cl_id).paginate(per_page=per_page, page=page, error_out=False)
    fatwas.extend(vol_fatwas)

    quest_fatwas = QuestFatwa.query.with_entities(QuestFatwa.class_id, QuestFatwa.question, QuestFatwa.answer). \
        filter(QuestFatwa.class_id == cl_id, QuestFatwa.answer != None).paginate(per_page=per_page, page=page, error_out=False)
    fatwas.extend(quest_fatwas)

    fatwa = Fatwa.query.with_entities(Fatwa.class_id, Fatwa.question, Fatwa.answer). \
        filter_by(class_id=cl_id).paginate(per_page=per_page, page=page, error_out=False)
    fatwas.extend(fatwa)
    max_pagination = vol_fatwas
    if quest_fatwas.total > max_pagination.total:
        max_pagination = quest_fatwas
    if fatwa.total > max_pagination.total:
        max_pagination = fatwa
    return fatwas, max_pagination
