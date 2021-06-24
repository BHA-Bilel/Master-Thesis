from flask import current_app, url_for
from flask_babel import force_locale, _
from flask_login import current_user
from flask_mail import Message

from webapp import mail, FatwaClass
from webapp.long_constant_text import MUFTI_ACCOUNT_PRIVILEGES, ADMIN_ACCOUNT_PRIVILEGES, USER_ACCOUNT_PRIVILEGES
from webapp.model.utils import zipfolder
from webapp.models import User, Role, UserRole
from webapp.utils import translate


def send_cl_rep(classification_report):
    role = Role.query.filter_by(name='Admin').first()
    usrs_wth_ad_role = UserRole.query.filter_by(role_id=role.id).all()
    admins = []
    for ad_role in usrs_wth_ad_role.items:
        admin = User.query.filter_by(id=ad_role.user_id).first()
        admins.append(admin)
    for admin in admins:
        with force_locale(admin.pref_lang):
            msg = Message(_('Classification report'), sender=current_app.config['MAIL_USERNAME'], recipients=[admin.email])
            lines = [_("Hello admin %(username)s, we hope you're doing well,", username=admin.username),
                     _('The classification model was successfully trained.'),
                     _('models folder and classification_report are attached to this email for maintenance reasons.')]

            msg.body = f'''{lines[0]}
{lines[1]}
{lines[2]}'''
            msg.attach(data=classification_report.getvalue(), filename='classification_report.csv', content_type='text/csv')

            memory_file = zipfolder()
            msg.attach(data=memory_file.getvalue(), filename='models.zip', content_type='application/zip')
            mail.send(msg)


def send_sim_rep(cl_name, data_number):
    role = Role.query.filter_by(name='Admin').first()
    usrs_wth_ad_role = UserRole.query.filter_by(role_id=role.id).all()
    admins = []
    for ad_role in usrs_wth_ad_role.items:
        admin = User.query.filter_by(id=ad_role.user_id).first()
        admins.append(admin)
        with force_locale(admin.pref_lang):
            msg = Message(_('Similarity report'), sender=current_app.config['MAIL_USERNAME'], recipients=[admin.email])
            lines = [_("Hello admin %(username)s, we hope you're doing well,", username=admin.username),
                     _('The similarity models of %(topic)s were successfully trained, they are trained now with %(data_num)s fatwas.',
                       topic=translate(fatwa_class=cl_name), data_num=data_number),
                     _('models folder is attached to this email for maintenance reasons.')]

            msg.body = f'''{lines[0]}
{lines[1]}
{lines[2]}'''
            memory_file = zipfolder()
            msg.attach(data=memory_file.getvalue(), filename='models.zip', content_type='application/zip')
            mail.send(msg)


def send_answered_question(user, question, id):
    with force_locale(user.pref_lang):
        msg = Message(_('Answered question'), sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
        lines = [_('The question you asked earlier:'), _('Has been answered by a mufti.'), _('You can view the fatwa in the following link:')]
        msg.body = f'''{lines[0]}
{question}
{lines[1]}
{lines[2]}
{url_for('fatwas.fatwa', id=id, _external=True)}
    '''
        mail.send(msg)


def send_quest_sum(eligible):
    muftis = User.query.with_entities(User.username, User.email, User.pref_lang).all()
    for mufti in muftis:
        with force_locale(mufti.pref_lang):
            msg = Message(_('Call for work'), sender=current_app.config['MAIL_USERNAME'], recipients=[mufti.email])
            lines = [_("Hello %(username)s, we hope you're doing well,", username=mufti.username),
                     _('Users have submitted new questions regarding these topics:'),
                     _('Please login to answer them, thank you.')]
            sum = []
            for el in eligible:
                sum.append(_('%(topic)s with %(num)s fatwas', num=eligible[el], topic=translate(fatwa_class=el)))

            msg.body = f'''{lines[0]}
{lines[1]}
'''
            for s in sum:
                msg.body += f'''
{s}
'''
            msg.body += f'''
{lines[2]}'''
            mail.send(msg)


def send_verify_email(user_id=None, username=None, email=None):
    if user_id and username and email:
        token = User.get_token(user_id=user_id)
        msg = Message(_('Email validation'), sender=current_app.config['MAIL_USERNAME'], recipients=[email])
        lines = [_('Your email was used in the registration of this account:'),
                 _('Enter the link below to validate your email address and start using your account:'),
                 _('If you did not register, then simply ignore this email')]
        msg.body = f'''{lines[0]}
        {url_for('users.profile', username=username, _external=True)}
        {lines[1]}
        {url_for('users.confirm_email', token=token, _external=True)}
        {lines[2]}
            '''
    else:
        token = User.get_token(user=current_user)
        url_link = None
        if current_user.is_mufti():
            url_link = 'users.profile'
        elif current_user.is_user():
            url_link = 'users.profile'
        with force_locale(current_user.pref_lang):
            msg = Message(_('Email validation'), sender=current_app.config['MAIL_USERNAME'], recipients=[current_user.email])
            lines = [_('Your email was used in the registration of this account:'),
                     _('Enter the link below to validate your email address and start using your account:'),
                     _('If you did not register, then simply ignore this email')]
            if url_link:
                msg.body = f'''{lines[0]}
{url_for(url_link, username=current_user.username, _external=True)}
{lines[1]}
{url_for('users.confirm_email', token=token, _external=True)}
{lines[2]}
    '''
            else:
                msg.body = f'''{lines[0]}
{lines[1]}
{url_for('users.confirm_email', token=token, _external=True)}
{lines[2]}
                    '''
    mail.send(msg)


def send_reset_email(user):
    token = User.get_token(user=user)

    with force_locale(user.pref_lang):
        msg = Message(_('Password Reset Request'), sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
        lines = [_('To reset your password, visit the following link:'),
                 _('If you did not make this request, then simply ignore this email and no changes will be made')]
        msg.body = f'''{lines[0]}
{url_for('users.reset_token', token=token, _external=True)}
{lines[1]}
        '''
        mail.send(msg)


def send_unbanned_email(pref_lang, email, username):
    with force_locale(pref_lang):
        msg = Message(_('Account Unbanned'), sender=current_app.config['MAIL_USERNAME'], recipients=[email])
        lines = [_("Hello user, we hope you're doing well,"),
                 _('We are happy to announce you that your account is no longer banned,'),
                 _('You can access your account:'),
                 url_for('users.profile', username=username, _external=True),
                 _("We're sorry for any misunderstanding from our part,"),
                 _('AFA Team.')]
        for line in lines:
            msg.body += f'''
    {line}'''
        mail.send(msg)


def send_banned_email(pref_lang, email, username):
    with force_locale(pref_lang):
        msg = Message(_('Account Banned'), sender=current_app.config['MAIL_USERNAME'], recipients=[email])
        lines = [_("Hello user,"),
                 _('We are sorry to announce you that your account has been banned by the administration'),
                 _('You can no longer access your account:'),
                 url_for('users.profile', username=username, _external=True),
                 _("If you think we made a mistake, please contact us in the following email: %(email)s", email=current_app.config['CONTACT_EMAIL']),
                 _("And we'll unban your account,"),
                 _('AFA Team.')]
        for line in lines:
            msg.body += f'''
    {line}'''
        mail.send(msg)


def send_demote_email(pref_lang, role, email, username):
    with force_locale(pref_lang):
        msg = Message(_('Account Demoted'), sender=current_app.config['MAIL_USERNAME'], recipients=[email])
        lines = [_("Hello user, we hope you're doing well,"),
                 _('We brought you bad news, your account has been demoted from %(role)s', role=role),
                 _('The link to your account:'),
                 url_for('users.profile', username=username, _external=True),
                 _("You can still use your other privileges if you're not banned,"),
                 _('Good luck in your journey, AFA Team.')]
        for line in lines:
            msg.body += f'''
    {line}'''
        mail.send(msg)


def send_promote_email(pref_lang, role, email, username):
    with force_locale(pref_lang):
        msg = Message(_('Account Promoted'), sender=current_app.config['MAIL_USERNAME'], recipients=[email])
        lines = [_("Hello user, we hope you're doing well"),
                 _('We brought you good news, your account has been promoted to %(role)s', role=role),
                 _('The link to your account:'),
                 url_for('users.profile', username=username, _external=True)]
        privileges = []
        if role == 'Admin':
            privileges = ADMIN_ACCOUNT_PRIVILEGES
        elif role == 'Mufti':
            privileges = MUFTI_ACCOUNT_PRIVILEGES
        for pr in privileges:
            lines.append(pr.text)
        lines.append(_('You can still use your other privileges if you login with @Role in the login page,'))
        lines.append(_('Good luck in your journey, AFA Team.'))
        for line in lines:
            msg.body += f'''
{line}'''
        mail.send(msg)


def send_request_email(username, proof, detail):
    with force_locale(current_app.config['CONTACT_EMAIL_PREF_LANG']):
        msg = Message(_('Mufti Request'), sender=current_app.config['MAIL_USERNAME'], recipients=[current_app.config['CONTACT_EMAIL']])
        lines = [_("Hello admin, we hope you're doing well,"),
                 _('This user is requesting to be a mufti in our website:'),
                 {url_for('users.profile', username=username, _external=True)},
                 _('The proof of his profession is attached to this email'),
                 _('The following are more details to justify his intentions'),
                 detail]

        for line in lines:
            msg.body += f'''
{line}'''
        msg.attach(data=proof, filename='proof.jpg', content_type='image/jpg')

        mail.send(msg)

#
# def send_model_sum(fatwa_class, data_number, classification_report=None):
#     admin_ac = FatwaClass.query.filter_by(name='Admin').first()
#     admin = User.query.filter_by(type=admin_ac).first()
#     with force_locale(admin.pref_lang):
#         msg = Message(_('Models update'), sender=current_app.config['MAIL_USERNAME'], recipients=[admin.email])
#         lines = [_('Hello admin %(username)s, we hope you are doing well,', username=admin.username),
#                  _('Muftis have submitted new fatwas regarding the topic of %(topic)s.', topic=translate(fatwa_class=fatwa_class)),
#                  _('Therefore the similarity models were automatically updated, they are trained now with %(data_num)s fatwas',
#                    data_num=data_number) + ',' if classification_report else '.', ]
#         if classification_report:
#             lines.append(_('the classification model was also updated.'))
#         lines.append(_('models folder and classification_report are attached to this email for maintenance reasons.'))
#
#         if classification_report:
#             msg.body = f'''{lines[0]}
# {lines[1]}
# {lines[2]}
# {lines[3]}
# {lines[4]}'''
#             msg.attach(data=classification_report.getvalue(), filename='classification_report.csv', content_type='text/csv')
#         else:
#             msg.body = f'''{lines[0]}
# {lines[1]}
# {lines[2]}
# {lines[3]}'''
#         memory_file = zipfolder()
#         msg.attach(data=memory_file.getvalue(), filename='models.zip', content_type='application/zip')
#         mail.send(msg)


# def send_delete_vol(user, fatwa_link, reason=None, ban=False):
#     with force_locale(user.pref_lang):
#         msg = Message(_('Deleted fatwa'), sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
#         lines = []
#         if ban:
#             lines = [_('You have so many banned fatwas,'),
#                      _('Thus, we are sorry to announce that we no longer accept fatwas from your account')]
#         lines.extend([_('The fatwa you added earlier from this link:'), _('Has been deleted by an admin or a mufti!')])
#         if reason and ban:
#             lines.append(_('For the following reason:'))
#             msg.body = f'''{lines[0]}
# {lines[1]}
# {lines[2]}
# {fatwa_link}
# {lines[3]}
# {reason}'''
#         elif reason:
#             lines.append(_('For the following reason:'))
#             msg.body = f'''{lines[0]}
# {fatwa_link}
# {lines[1]}
# {lines[2]}
# {reason}'''
#         else:
#             lines.append(_('Please consider adding good fatwas next time, or you will get banned !'))
#             msg.body = f'''{lines[0]}
# {fatwa_link}
# {lines[1]}
# {lines[2]}'''
#
#         mail.send(msg)


# def send_validated_fatwa(user):
#     with force_locale(user.pref_lang):
#         msg = Message(_('Validated fatwas'), sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
#         lines = [_('All the fatwas you volunteered earlier has been validated by muftis,'), _('Thank you for contributing to the website.')]
#         msg.body = f'''{lines[0]}
# {lines[1]}
# {lines[2]}'''
#         mail.send(msg)


# def send_vol_sum(fatwa_class, vol):
#     muftis = User.query.with_entities(User.username, User.email, User.pref_lang).all()
#     for mufti in muftis:
#         with force_locale(mufti.pref_lang):
#             msg = Message(_('Call for work'), sender=current_app.config['MAIL_USERNAME'], recipients=[mufti.email])
#             lines = [_('Hello %(username)s, we hope you are doing well,', username=mufti.username),
#                      _('Users have submitted %(num)s new voluntary fatwas regarding the topic of %(topic)s', num=vol,
#                        topic=translate(fatwa_class=fatwa_class)),
#                      _('Please login and enter this link to validate them, thank you.')]
#             msg.body = f'''{lines[0]}
# {lines[1]}
# {lines[2]}
# {url_for('vol_fatwas.all_vol_fatwas', fatwa_class=fatwa_class, _external=True)}
#             '''
#             mail.send(msg)


# def send_delete_question(user, question, reason=None, ban=False):
#     with force_locale(user.pref_lang):
#         msg = Message(_('Deleted question'), sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
#         lines = []
#         if ban:
#             lines = [_('You have so many banned questions,'),
#                      _('Thus, we are sorry to announce that we no longer accept questions from your account')]
#         lines.extend([_('The question you asked earlier:'), _('Has been deleted by an admin or a mufti!')])
#         if reason and ban:
#             lines.append(_('For the following reason:'))
#             msg.body = f'''{lines[0]}
# {lines[1]}
# {lines[2]}
# {question}
# {lines[3]}
# {reason}'''
#         elif reason:
#             lines.append(_('For the following reason:'))
#             msg.body = f'''{lines[0]}
# {question}
# {lines[1]}
# {lines[2]}
# {reason}'''
#         else:
#             lines.append(_('Please consider asking relevant questions next time, or you will get banned !'))
#             msg.body = f'''{lines[0]}
# {question}
# {lines[1]}
# {lines[2]}'''
#
#         mail.send(msg)
