from flask import url_for, Markup
from wtforms import TextAreaField, SubmitField, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import URLField
from wtforms.validators import Length, url, DataRequired
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

from webapp.models import FatwaClass, Website, VolFatwa, Fatwa, QuestFatwa

from webapp.vol_fatwas.utils import get_domain
from langdetect import detect

from flask_wtf import FlaskForm

from flask_babel import lazy_gettext as _l


class VolFatwaForm(FlaskForm):
    fatwa_class = QuerySelectField(_l('Select fatwa class'), query_factory=FatwaClass.query, allow_blank=False, get_label='name')
    link = URLField(validators=[DataRequired(), url()])
    question = TextAreaField(_l('QuestFatwa'), validators=[DataRequired(), Length(min=5, max=250)])
    answer = TextAreaField(_l('Answer'), validators=[DataRequired(), Length(min=10, max=250)])
    submit = SubmitField(_l('Ask question'))

    def validate_question(self, question):
        if detect(question.data) is not 'ar':
            raise ValidationError(_l('Question must be in arabic letters only'))
        try:
            site = self.link.data
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = Request(site, headers=hdr)
            page = urlopen(req)
            soup = BeautifulSoup(page, features="lxml")

            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            quest = question.data
            quest = quest.replace('\n', ' ')
            if quest not in text:
                raise ValidationError(_l('This question does not exist in the given link!'))
        except:
            pass
        vol_fatwa = VolFatwa.query.filter(VolFatwa.question == question.data, VolFatwa.validated_on != None).first()
        if vol_fatwa:
            raise ValidationError(_l('This question has already been volunteered by a user' + Markup(
                f' <a href={url_for("quest_fatwas.quest_fatwa", id=vol_fatwa.id)} class="alert-link">' + _l(
                    'Here') + '</a>')))

        quest_fatwa = QuestFatwa.query.filter(QuestFatwa.question == question.data, QuestFatwa.answered_on != None).first()
        if quest_fatwa:
            raise ValidationError(_l('This question has already been answered by a mufti' + Markup(
                f' <a href={url_for("quest_fatwas.quest_fatwa", id=quest_fatwa.id)} class="alert-link">' + _l(
                    'Here') + '</a>')))

        fatwa = Fatwa.query.filter_by(question=question.data).first()
        if fatwa:
            raise ValidationError(_l('This question has already been added by a mufti' + Markup(
                f' <a href={url_for("quest_fatwas.quest_fatwa", id=fatwa.id)} class="alert-link">' + _l(
                    'Here') + '</a>')))

    def validate_answer(self, answer):
        if detect(answer.data) is not 'ar':
            raise ValidationError(_l('Answer must be in arabic letters only'))
        try:
            site = self.link.data
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = Request(site, headers=hdr)
            page = urlopen(req)
            soup = BeautifulSoup(page, features="lxml")

            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            ans = answer.data
            ans = ans.replace('\n', ' ')
            if ans not in text:
                raise ValidationError(_l('This answer does not exist in the given link!'))
        except:
            pass

    def validate_link(self, link):
        website = Website.query.filter_by(domain=get_domain(link.data)).first()
        if website and website.banned:
            raise ValidationError(_l('We do not accept fatwas from this website'))
        vol_fatwa = VolFatwa.query.filter_by(link=link.data).first()
        if vol_fatwa:
            raise ValidationError(_l('This link already exists in the database' + Markup(
                f' <a href={url_for("quest_fatwas.quest_fatwa", id=vol_fatwa.id)} class="alert-link">' + _l(
                    'Here') + '</a>')))
