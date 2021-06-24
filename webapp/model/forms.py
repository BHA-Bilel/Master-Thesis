from flask_wtf import FlaskForm
from wtforms import SubmitField, ValidationError, FileField
from wtforms.validators import DataRequired

from webapp.utils import translate
from webapp.models import FatwaClass
from flask_babel import lazy_gettext as _l


class UploadModelsForm(FlaskForm):
    file = FileField(_l('Browse files'), validators=[DataRequired()])
    upload_models = SubmitField(_l('Upload models'))

    def validate_file(self, file):
        if '.' in file.data.filename and file.data.filename.rsplit('.', 1)[1].lower() == 'zip':
            pass
        else:
            raise ValidationError(_l('Only zip files are allowed !'))


class TrainForm(FlaskForm):
    all_classes = FatwaClass.query.all()
    choices = []
    for cl in all_classes:
        choices.append((cl.id, translate(fatwa_class=cl.name)))
    download = SubmitField(_l('Download models'))
    train_sim = SubmitField(_l('Check for similarity train'))
    train_cl = SubmitField(_l('Check for classification train'))
