from datetime import datetime

from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from webapp import db, ctx, bcrypt


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    owners = db.relationship('UserRole', backref='role', lazy=True)

    def __repr__(self):
        return f"Role('{self.id}', ''{self.name}')"


class UserRole(db.Model):
    _tablename__ = 'user_roles'

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    pref_lang = db.Column(db.String(2), default='fr', nullable=False)

    roles = db.relationship('UserRole', backref='user_role', lazy=True)

    ver_em = db.Column(db.Boolean, default=False, nullable=False)
    banned = db.Column(db.Boolean, default=False, nullable=False)
    ban_quest = db.Column(db.Boolean, default=False, nullable=False)
    ban_vol = db.Column(db.Boolean, default=False, nullable=False)

    fatwas = db.relationship('Fatwa', backref='author', lazy=True)
    vol_fatwas = db.relationship('VolFatwa', backref='volunteer', lazy=True)
    quest_fatwas = db.relationship('QuestFatwa', backref='asker', lazy=True)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_log = db.Column(db.DateTime, nullable=True)

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


class FatwaClass(db.Model):
    __tablename__ = 'fatwa_class'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)

    fatwas = db.relationship('Fatwa', backref='fatwa_class', lazy=True)
    quest_fatwas = db.relationship('QuestFatwa', backref='fatwa_class', lazy=True)
    vol_fatwas = db.relationship('VolFatwa', backref='fatwa_class', lazy=True)
    cl_annexes = db.relationship('ClAnnex', backref='fatwa_class', lazy=True)
    sim_annexes = db.relationship('SimAnnex', backref='fatwa_class', lazy=True)

    def __repr__(self):
        return f"Fatwa Class('{self.id}', ''{self.name}')"

    @staticmethod
    def all_fatwa_classes():
        return FatwaClass.query.all()


class Fatwa(db.Model):
    __tablename__ = 'fatwas'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('fatwa_class.id'), nullable=False)
    mufti_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    question = db.Column(db.Text, unique=True, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Fatwa('{self.id}', '{self.mufti_id}', '{self.question}')"


class QuestFatwa(Fatwa):
    __tablename__ = 'quest_fatwas'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mufti_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    answer = db.Column(db.Text, nullable=True)

    email_notif = db.Column(db.Boolean, default=True, nullable=False)
    anonyn = db.Column(db.Boolean, default=False, nullable=False)
    answered_on = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    def __repr__(self):
        return f"QuestFatwa('{self.id}', '{self.user_id}', '{self.question}')"


class DelQuestion(db.Model):
    __tablename__ = 'del_questions'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class DelVolFatwa(db.Model):
    __tablename__ = 'del_vol_fatwas'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Website(db.Model):
    __tablename__ = 'websites'

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    taken_fatwas = db.relationship('VolFatwa', backref='website', lazy=True)


class VolFatwa(Fatwa):
    __tablename__ = 'vol_fatwas'

    mufti_id = None
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    link = db.Column(db.String(100), unique=True, nullable=False)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=True)

    def __repr__(self):
        return f"Voluntary Fatwa('{self.id}', '{self.user_id}', '{self.question}')"


class ClTrain(db.Model):
    __tablename__ = 'cl_train'
    id = db.Column(db.Integer, primary_key=True)
    minority_class = db.Column(db.Integer, db.ForeignKey('fatwa_class.id'), nullable=False)
    data_per_class = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    learning_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    annexes = db.relationship('ClAnnex', backref='classes', lazy=True)

    def __repr__(self):
        return f"Classification Training('{self.id}', ''{self.data_per_class}', ''{self.learning_date}')"


class ClAnnex(db.Model):
    __tablename__ = 'cl_ann'
    train_id = db.Column(db.Integer, db.ForeignKey('cl_train.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('fatwa_class.id'), nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"ClAnnex('{self.id}', '{self.learning_date}'', '{self.data_per_class}''{self.accuracy}', '{self.percision}'', '{self.f1_score}')"


class SimAnnex(db.Model):
    __tablename__ = 'sim_ann'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('fatwa_class.id'), nullable=False)
    learning_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_number = db.Column(db.Float, nullable=False)

    # for each fatwa_class we take fatwas from 3 tables: vol_fatwas, fatwas, quest_fatwas in that order
    # only one entry is sufficient for each fatwa_class
    # the id returned by the sim models (id) will be compared to the next two variables:
    last_vol_id = db.Column(db.Integer, nullable=False)
    first_quest_id = db.Column(db.Integer, nullable=False)

    # if id <= last_vol_id: get fatwa from vol_fatwas table where vol_id=id
    # elif id >= first_quest_id: get fatwa from quest_fatwas table where quest_id=id-first_quest_id
    # else: get fatwa from fatwas where fat_id=id-last_vol_id

    def __repr__(self):
        return f"SimAnnex('{self.id}', '{self.learning_date}'', '{self.data_number}')"
