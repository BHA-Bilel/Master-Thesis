from flask import url_for, Markup
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length
from flask_babel import lazy_gettext as _l

from webapp.models import FatwaClass, QuestFatwa, VolFatwa, Fatwa
from langdetect import detect


class FatwaForm(FlaskForm):
    fatwa_class = QuerySelectField(_l('Select fatwa class'), query_factory=FatwaClass.query, allow_blank=False, get_label='name')
    question = TextAreaField(_l('Question'), validators=[DataRequired(), Length(min=5, max=250)])
    answer = TextAreaField(_l('Answer'), validators=[DataRequired(), Length(min=10, max=250)])
    submit = SubmitField(_l('Submit'))

    def validate_question(self, question):
        if detect(question.data) is not 'ar':
            raise ValidationError(_l('Question must be in arabic letters only'))
        quest_fatwa = QuestFatwa.query.filter(QuestFatwa.question == question.data, QuestFatwa.answered_on != None).first()
        if quest_fatwa:
            raise ValidationError(_l('This question has already been answered by a mufti' + Markup(
                f' <a href={url_for("quest_fatwas.quest_fatwa", id=quest_fatwa.id)} class="alert-link">' + _l(
                    'Here') + '</a>')))

        vol_fatwa = VolFatwa.query.filter(VolFatwa.question == question.data, VolFatwa.validated_on != None).first()
        if vol_fatwa:
            raise ValidationError(_l('This question has already been volunteered by a user' + Markup(
                f' <a href={url_for("quest_fatwas.quest_fatwa", id=vol_fatwa.id)} class="alert-link">' + _l(
                    'Here') + '</a>')))

        fatwa = Fatwa.query.filter_by(question=question.data).first()
        if fatwa:
            raise ValidationError(_l('This question has already been added by a mufti' + Markup(
                f' <a href={url_for("quest_fatwas.quest_fatwa", id=fatwa.id)} class="alert-link">' + _l(
                    'Here') + '</a>')))

    def validate_answer(self, answer):
        if detect(answer.data) is not 'ar':
            raise ValidationError(_l('Answer must be in arabic letters only'))
