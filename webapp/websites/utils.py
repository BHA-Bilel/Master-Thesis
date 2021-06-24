import zipfile
from csv import DictWriter
from io import StringIO, BytesIO

from flask_login import current_user

from webapp import FatwaClass, db
from sqlalchemy.exc import IntegrityError
from webapp.models import Website, VolFatwa


def get_download_websites(website_id=0):
    if website_id > 0:
        return Website.query.filter_by(id=website_id).all()
    else:
        return Website.query.all()


def get_websites_summary(page):
    websites = Website.query.order_by(Website.taken_fatwas.desc()).paginate(per_page=20, page=page, error_out=True)
    summary = []
    for website in websites:
        summary.append({'domain': website.domain, 'taken_fatwas': len(website.taken_fatwas)})
    return summary, websites


def get_websites(page):
    return Website.query.order_by(Website.taken_fatwas.desc()).paginate(per_page=20, page=page, error_out=True)


def get_fatwas(page, website):
    # todo change datetime to user's local time
    return website.taken_fatwas.order_by(VolFatwa.id.desc()).paginate(per_page=20, page=page, error_out=True)


def count_websites():
    return Website.query.count()


def count_taken_fatwas(website_id):
    return VolFatwa.query.filter_by(website_id=website_id).count()


def upload_websites_fatwas(website_id, csv_file, csv_reader):
    csv_file.seek(0)
    next(csv_reader)
    vol_fatwas = []

    all_classes = FatwaClass.query.all()
    class_to_id = dict()
    for row in all_classes:
        class_to_id[row.name] = row.id

    i = 0
    for row in csv_reader:
        # todo change link to row[x]
        class_id = class_to_id[row[0]]
        if not class_id:
            class_id = class_to_id['Unclassified']
        vol_fatwa = VolFatwa(question=row[1], answer=row[2], class_id=class_id, website_id=website_id,
                             link='unknown-' + str(i), user_id=current_user.id)
        i += 1
        vol_fatwas.append(vol_fatwa)
    insert_vol_fatwas(vol_fatwas=vol_fatwas)


def insert_vol_fatwas(vol_fatwas):
    for vol_fatwa in vol_fatwas:
        try:
            db.session.add(vol_fatwa)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def export_websites_fatwas(domain, taken_fatwas):
    new_csvfile = StringIO()
    new_csvfile.name = domain
    columns = ['website_id', 'topic', 'question', 'answer']
    writer = DictWriter(new_csvfile, fieldnames=columns)
    writer.writeheader()
    all_classes = FatwaClass.query.all()
    class_to_id = dict()
    for row in all_classes:
        class_to_id[row.name] = row.id

    for data in taken_fatwas:
        writer.writerow({'website_id': data.id, 'topic': class_to_id[data.class_id], 'question': data.question, 'answer': data.answer})
    new_csvfile.seek(0)
    return new_csvfile


def zipfiles(files):
    data = BytesIO()
    with zipfile.ZipFile(data, 'w', zipfile.ZIP_DEFLATED) as zipobj:
        for file in files:
            zipobj.write(file)
    data.seek(0)
    return data
