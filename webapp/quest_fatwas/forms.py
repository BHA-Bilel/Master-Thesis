from flask import url_for, Markup
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, ValidationError, BooleanField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length

from webapp.models import FatwaClass, VolFatwa, QuestFatwa, Fatwa
from flask_babel import lazy_gettext as _l
from langdetect import detect


class QuestFatwaForm(FlaskForm):
    fatwa_class = QuerySelectField(_l('Select fatwa class'), query_factory=FatwaClass.query, allow_blank=False, get_label='name')
    question = TextAreaField(_l('QuestFatwa'), validators=[DataRequired(), Length(min=5, max=250)])
    anonym = BooleanField(_l('Ask this question anonymously'))
    email_notif = BooleanField(_l('Notify me when this question is answered'))
    submit = SubmitField(_l('Ask question'))

    def validate_question(self, question):
        if detect(question.data) is not 'ar':
            raise ValidationError(_l('Question must be in arabic letters only'))
        quest_fatwa = QuestFatwa.query.filter(QuestFatwa.question == question.data, QuestFatwa.mufti_id != None).first()
        if quest_fatwa:
            raise ValidationError(_l('This question has already been answered by a mufti' + Markup(
                f' <a href={url_for("quest_fatwas.quest_fatwa", id=quest_fatwa.id)} class="alert-link">' + _l(
                    'Here') + '</a>')))

        quest_fatwa = QuestFatwa.query.filter(QuestFatwa.question == question.data, QuestFatwa.mufti_id == None).first()
        if quest_fatwa:
            if quest_fatwa.user_id == current_user.id:
                raise ValidationError(_l('You already asked this question' + Markup(
                    f' <a href={url_for("quest_fatwas.quest_fatwa", id=quest_fatwa.id)} class="alert-link">' + _l(
                        'Here') + '</a>')))
            else:
                raise ValidationError(_l('This question has already been asked by a user, please ask another one.'))

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
