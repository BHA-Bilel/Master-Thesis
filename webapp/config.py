import os


class Config:
    # .secrets
    # secrets.token_hex(16)
    # SECRET_KEY='5a92ed2fa5ad1b3749576783c55e27c6'
    # SQLALCHEMY_DATABASE_URI='sqlite:///site.db'

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODELS_PATH = r'webapp\qasystem\model\models'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    LANGUAGES = ['en', 'fr', 'ar']
    CONTACT_EMAIL_PREF_LANG = 'en'
    MODELS_TRAINING = False
    MIN_QASYSTEM_SIM = 0.5
    MAX_DOC_ORDER = 5
    # SESSION_COOKIE_SECURE = True
    # REMEMBER_COOKIE_SECURE = True
    # SESSION_COOKIE_HTTPONLY = True
    # REMEMBER_COOKIE_HTTPONLY = True
