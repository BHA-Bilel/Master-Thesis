from webapp import db, ctx
from webapp.models import Fatwa, SimAnnex, ClAnnex


class Hadj(Fatwa):
    __tablename__ = 'hadjs'
    id = db.Column(db.Integer, primary_key=True)
    mufti_id = db.Column(db.Integer, db.ForeignKey('muftis.id'), nullable=False)

    def __repr__(self):
        return f"Hadj('{self.id}', '{self.mufti_id}'', '{self.question}')"


class HadjSimAnnex(SimAnnex):
    __tablename__ = 'hadjsimannex'
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"HadjSimAnnex('{self.id}', '{self.learning_date}'', '{self.data_number}')"


class HadjClAnnex(ClAnnex):
    __tablename__ = 'hadjclannex'
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"HadjClAnnex('{self.id}', '{self.learning_date}'', '{self.data_per_class}''{self.accuracy}', '{self.percision}'', '{self.f1_score}')"


class Salat(Fatwa):
    __tablename__ = 'salats'
    id = db.Column(db.Integer, primary_key=True)
    mufti_id = db.Column(db.Integer, db.ForeignKey('muftis.id'), nullable=False)

    def __repr__(self):
        return f"Salat('{self.id}', '{self.mufti_id}'', '{self.question}')"


class SalatSimAnnex(SimAnnex):
    __tablename__ = 'salatsimannex'
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"SalatSimAnnex('{self.id}', '{self.learning_date}'', '{self.data_number}')"


class SalatClAnnex(ClAnnex):
    __tablename__ = 'salatclannex'
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"SalatClAnnex('{self.id}', '{self.learning_date}'', '{self.data_per_class}''{self.accuracy}', '{self.percision}'', '{self.f1_score}')"


class Sawm(Fatwa):
    __tablename__ = 'sawms'
    id = db.Column(db.Integer, primary_key=True)
    mufti_id = db.Column(db.Integer, db.ForeignKey('muftis.id'), nullable=False)

    def __repr__(self):
        return f"Sawm('{self.id}', '{self.mufti_id}'', '{self.question}')"


class SawmSimAnnex(SimAnnex):
    __tablename__ = 'sawmsimannex'
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"SawmSimAnnex('{self.id}', '{self.learning_date}'', '{self.data_number}')"


class SawmClAnnex(ClAnnex):
    __tablename__ = 'sawmclannex'
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"SawmClAnnex('{self.id}', '{self.learning_date}'', '{self.data_per_class}''{self.accuracy}', '{self.percision}'', '{self.f1_score}')"


class Zakat(Fatwa):
    __tablename__ = 'zakats'
    id = db.Column(db.Integer, primary_key=True)
    mufti_id = db.Column(db.Integer, db.ForeignKey('muftis.id'), nullable=False)

    def __repr__(self):
        return f"Zakat('{self.id}', '{self.mufti_id}'', '{self.question}')"


class ZakatSimAnnex(SimAnnex):
    __tablename__ = 'zakatsimannex'
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"ZakatSimAnnex('{self.id}', '{self.learning_date}'', '{self.data_number}')"


class ZakatClAnnex(ClAnnex):
    __tablename__ = 'zakatclannex'
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"ZakatClAnnex('{self.id}', '{self.learning_date}'', '{self.data_per_class}''{self.accuracy}', '{self.percision}'', '{self.f1_score}')"


# with ctx:
#     db.create_all()
