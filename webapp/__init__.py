# from flask_paranoid.Paranoid

from flask import Flask
from sqlalchemy.exc import IntegrityError

from webapp.config import Config
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_babel import Babel, _

from webapp.models import Role, User, FatwaClass, UserRole

bootstrap = Bootstrap()
db = SQLAlchemy()
engine = db.create_engine(Config.SQLALCHEMY_DATABASE_URI, {})
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message = _('Please login to access this page')
login_manager.login_message_category = 'info'
mail = Mail()
babel = Babel()
# login_manager.session_protection = "strong"

# paranoid = Paranoid(app)
# paranoid.redirect_view = '/'
# comment next line to use db in terminal

ctx = None


def create_app(config_class=Config):
    current_app = Flask(__name__)
    current_app.config.from_object(config_class)
    current_app.url_map.strict_slashes = False
    current_app.jinja_env.globals.update(all_fatwa_classes=FatwaClass.all_fatwa_classes)

    global ctx
    ctx = current_app.app_context()

    bootstrap.init_app(current_app)
    db.init_app(current_app)
    bcrypt.init_app(current_app)
    login_manager.init_app(current_app)
    mail.init_app(current_app)
    babel.init_app(current_app)

    from webapp.users.routes import users
    from webapp.administration.routes import administration

    from webapp.model.routes import model
    from webapp.qasystem.routes import qasystem
    from webapp.main.routes import main

    from webapp.fatwa_class.routes import fatwa_class
    from webapp.fatwas.routes import fatwas
    from webapp.quest_fatwas.routes import quest_fatwas
    from webapp.vol_fatwas.routes import vol_fatwas

    from webapp.errors.handlers import errors

    current_app.register_blueprint(users)
    current_app.register_blueprint(administration)

    current_app.register_blueprint(qasystem)
    current_app.register_blueprint(main)

    current_app.register_blueprint(fatwa_class)
    current_app.register_blueprint(fatwas)
    current_app.register_blueprint(quest_fatwas)
    current_app.register_blueprint(vol_fatwas)

    current_app.register_blueprint(errors)

    from webapp.scheduled_tasks import start_scheduler, save_config
    start_scheduler()
    config = {
        # for cl training
        'min_data_per_class': 100,

        # to restrict users
        'del_quest_ban': 20,
        'del_vol_ban': 5}
    save_config(config=config)

    # db.drop_all()
    db.create_all()
    try:
        admin = Role(name='Admin')
        db.session.add(admin)

        mufti = Role(name='Mufti')
        db.session.add(mufti)

        user = Role(name='User')
        db.session.add(user)
        unclassified = FatwaClass(name='Unclassified', description='todo')
        db.session.add(unclassified)
        password_hash = bcrypt.generate_password_hash("123456789").decode('utf-8')
        me = User(fname='admin', lname='admin', username='admin', password=password_hash,
                  email='d4sterkiller@gmail.com', ver_em=True, pref_lang='en')
        db.session.add(me)
        db.session.commit()

        admin_role = UserRole(role_id=admin.id, user_id=me.id)
        user_role = UserRole(role_id=user.id, user_id=me.id)
        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()

        # todo create dummy users here

        hadj = FatwaClass(name='Hadj', description='')
        salat = FatwaClass(name='Sawm', description='')
        sawm = FatwaClass(name='Sawm', description='')
        zakat = FatwaClass(name='Zakat', description='')

        db.session.add(hadj)
        db.session.add(salat)
        db.session.add(sawm)
        db.session.add(zakat)

        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    return current_app
