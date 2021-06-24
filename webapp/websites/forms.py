from flask_wtf import FlaskForm
from wtforms import SubmitField, ValidationError, RadioField, FileField, TextAreaField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, url, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from webapp.models import Website
from flask_babel import lazy_gettext as _l


class WebsiteForm(FlaskForm):
    domain = URLField(_l('Website domain'), validators=[DataRequired(), url()])
    description = TextAreaField(_l('Description'), validators=[DataRequired(), Length(min=10, max=250)])
    submit = SubmitField(_l('Submit'))

    def validate_domain(self, domain):
        website = Website.query.filter_by(domain=domain.data).first()
        if website:
            raise ValidationError(_l('Website already exists'))


class UploadCorpForm(FlaskForm):
    domain = QuerySelectField(_l('Select website'), query_factory=Website.query.filter_by(trusted=True), allow_blank=False, get_label='domain')
    file = FileField(_l('Browse files'), validators=[DataRequired()])
    upload_corp = SubmitField(_l('Upload corpus'))

    def validate_file(self, file):
        if '.' in file.data.filename and file.data.filename.rsplit('.', 1)[1].lower() == 'csv':
            pass
        else:
            raise ValidationError(_l('Only csv files are allowed !'))
