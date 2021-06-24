from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp
from flask_babel import lazy_gettext as _l
from webapp.models import FatwaClass


class FatwaClassForm(FlaskForm):
    name = TextAreaField(_l('Name'), validators=[DataRequired(), Length(min=5, max=250),
                                                 Regexp('[a-zA-Z ]+', message=_l('Name must be in latin letters only'))])
    description = TextAreaField(_l('Description'), validators=[DataRequired(), Length(min=10, max=250)])
    submit = SubmitField(_l('Submit'))

    def validate_name(self, name):
        fatwa_class = FatwaClass.query.filter_by(name=name.data).first()
        if fatwa_class:
            raise ValidationError(_l('This fatwa class already exists'))
