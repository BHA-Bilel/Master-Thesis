from webapp import db, ctx, engine
from flask_login import UserMixin

from webapp.fatwas.fat_cls import Fatwa_Class
from webapp.models import Person, Question
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class HadjQuestion(Question):
    __tablename__ = 'hadjquestions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"HadjQuestion('{self.id}', ''{self.user_id}', '{self.question}')"


class SalatQuestion(Question):
    __tablename__ = 'salatquestions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"SalatQuestion('{self.id}', ''{self.user_id}', '{self.question}')"


class SawmQuestion(Question):
    __tablename__ = 'sawmquestions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"SawmQuestion('{self.id}', ''{self.user_id}', '{self.question}')"


class ZakatQuestion(Question):
    __tablename__ = 'zakatquestions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"ZakatQuestion('{self.id}', ''{self.user_id}', '{self.question}')"


class Mufti(Person, UserMixin):
    __tablename__ = 'muftis'
    id = db.Column(db.Integer, primary_key=True)
    banned = db.Column(db.Boolean, default=False, nullable=False)
    pref_lang = db.Column(db.String(2), default='ar', nullable=False)
    ver_em = db.Column(db.Boolean, default=False, nullable=False)
    hadj = db.relationship('Hadj', backref='author', lazy=True)
    salat = db.relationship('Salat', backref='author', lazy=True)
    sawm = db.relationship('Sawm', backref='author', lazy=True)
    zakat = db.relationship('Zakat', backref='author', lazy=True)

    @staticmethod
    def get_token(mufti=None, mufti_id=None, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        if mufti:
            return s.dumps({'mufti_id': mufti.id}).decode('utf-8')
        elif mufti_id:
            return s.dumps({'mufti_id': mufti_id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            mufti_id = s.loads(token)['mufti_id']
        except:
            return None
        return Mufti.query.get(mufti_id)

    def __repr__(self):  # toString equivalent
        return f"Mufti('{self.id}', ''{self.fname}', '{self.lname}')"


class User(Person, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    banned = db.Column(db.Boolean, default=False, nullable=False)
    pref_lang = db.Column(db.String(2), default='fr', nullable=False)
    ver_em = db.Column(db.Boolean, default=False, nullable=False)
    answered_hadj_quest = db.Column(db.Integer, default=0)
    answered_salat_quest = db.Column(db.Integer, default=0)
    answered_sawm_quest = db.Column(db.Integer, default=0)
    answered_zakat_quest = db.Column(db.Integer, default=0)

    hadj = db.relationship('HadjQuestion', backref='author', lazy=True)
    salat = db.relationship('SalatQuestion', backref='author', lazy=True)
    sawm = db.relationship('SawmQuestion', backref='author', lazy=True)
    zakat = db.relationship('ZakatQuestion', backref='author', lazy=True)

    @staticmethod
    def get_token(user=None, user_id=None, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        if user:
            return s.dumps({'user_id': user.id}).decode('utf-8')
        elif user_id:
            return s.dumps({'user_id': user_id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.id}', ''{self.fname}', '{self.lname}')"

# todo for each fatwa class
# class rep_fat(db.Model):
#     fatwa_class = db.Column(db.Enum(Fatwa_Class))
#     fatwa_id =  db.Column(db.Integer, db.ForeignKey('fatwas.id'), nullable=False)
#     mufti_id =  db.Column(db.Integer, db.ForeignKey('muftis.id'), nullable=False)

# todo for each question class
# class rep_quest(db.Model):
#     question_topic = db.Column(db.Enum(Fatwa_Class))
#     question_id =  db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
#     mufti_id =  db.Column(db.Integer, db.ForeignKey('muftis.id'), nullable=False)

# with ctx:
#     # db.drop_all()
#     db.create_all()
#     db.engine.execute('alter table muftis add column banned Boolean')
#     db.engine.execute('alter table user add column banned Boolean')
