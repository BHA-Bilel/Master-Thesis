from flask import current_app

from webapp import db, ctx, bcrypt
from flask_login import UserMixin
from webapp.models import Person
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Administrator(Person, UserMixin):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)

    def get_reset_token(admin, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'admin_id': admin.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            admin_id = s.loads(token)['admin_id']
        except:
            return None
        return Administrator.query.get(admin_id)

    def __repr__(self):
        return f"Admin('{self.id}', ''{self.fname}', '{self.lname}')"

# with ctx:
#     db.create_all()

# with ctx:
#     password_hash = bcrypt.generate_password_hash("123456789").decode('utf-8')
#     adm = Administrator(fname='admin', lname='admin', username='admin', password=password_hash, email='admin@gmail.com')
#     db.session.add(adm)
#     db.session.commit()
#     print('ADMIN ADDED TO DB')
