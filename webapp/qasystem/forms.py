from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length
from flask_babel import lazy_gettext as _l
from webapp.models import FatwaClass


class QueryForm(FlaskForm):
    fatwa = TextAreaField(_l('Fatwa'), validators=[DataRequired(), Length(min=5)])
    submit = SubmitField(_l('Pass query'))


class ClassForm(FlaskForm):
    fatwa_class = QuerySelectField(_l('Wrong classification? enter the right class below.'), query_factory=FatwaClass.query, allow_blank=True,
                                   get_label='name')
    submit = SubmitField(_l('Pass correct class'))
