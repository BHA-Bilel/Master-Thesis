from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, ValidationError, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

from webapp.models import User
from flask_login import current_user
from flask_babel import lazy_gettext as _l


class RequestMuftiForm(FlaskForm):
    proof = FileField(_l('Proof of profession'), validators=[DataRequired()])
    detail = TextAreaField(_l('More details'), validators=[DataRequired(), Length(min=10, max=250)])
    submit = SubmitField(_l('Submit'))


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    submit = SubmitField(_l('Login'))


class RegistrationForm(FlaskForm):
    fname = StringField(_l('First name'), validators=[DataRequired(), Length(min=4, max=50)])
    lname = StringField(_l('Last name'), validators=[DataRequired(), Length(min=4, max=50)])
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=5, max=20),
                                                       Regexp('[a-zA-Z0-9_]+', message=_l('only letters, numbers and underscores are allowed'))])
    password = PasswordField(_l('Password'), validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField(_l('Confirm password'), validators=[DataRequired(), Length(min=8, max=20), EqualTo('password')])
    email = StringField(_l("email"), validators=[DataRequired(), Email(), Length(min=8, max=60)])

    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_l('Username taken, please choose another one'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_l('Email already associated with a user, please choose another one'))


class UpdateAccountForm(FlaskForm):
    fname = StringField(_l('First name'), validators=[DataRequired(), Length(min=4, max=50)])
    lname = StringField(_l('Last name'), validators=[DataRequired(), Length(min=4, max=50)])
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=5, max=20),
                                                       Regexp('[a-zA-Z0-9_]+', message=_l('only letters, numbers and underscores are allowed'))])
    email = StringField(_l("email"), validators=[DataRequired(), Email(), Length(min=8, max=60)])
    submit = SubmitField(_l('Update'))

    def validate_username(self, username):
        if username.data != current_user.username:
            # todo
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(_l('Username taken, please choose another one'))

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data.lower()).first()
            if user:
                raise ValidationError(_l('Email already associated with a user, please choose another one'))


class RequestResetForm(FlaskForm):
    email = StringField(_l("email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is None:
            raise ValidationError(_l('There is no account with that email. You must register first.'))
        elif not user.ver_em:
            raise ValidationError(_l('You must verify your email first.'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField(_l('Confirm password'), validators=[DataRequired(), Length(min=8, max=20), EqualTo('password')])

    submit = SubmitField(_l('Reset Password'))
