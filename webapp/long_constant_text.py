# todo: add text of about page, home page, FAQ page, any constant long text
from flask_babel import _


class LongText:
    def __init__(self, tag, text):
        self.tag = tag
        self.text = text


# ----------------------------------------------------------------------------------------------------------------------------------------
#
#
#
#
#
ADMIN_ACCOUNT_PRIVILEGES = []

AD_AC_PR_LINE_1 = LongText(tag='p', text=_('Your new role as an admin has brought you a lot of control,'))
AD_AC_PR_LINE_2 = LongText(tag='p', text=_('But that control comes with duties to fulfill,'))
AD_AC_PR_LINE_3 = LongText(tag='p', text=_('As the administration of the website, we expect of you to:'))
AD_AC_PR_LINE_4 = LongText(tag='p', text=_('Do your best at maintaining the website,'))
AD_AC_PR_LINE_5 = LongText(tag='p', text=_('Ban bad users, even muftis if you had to!'))

ADMIN_ACCOUNT_PRIVILEGES.append(AD_AC_PR_LINE_1)
ADMIN_ACCOUNT_PRIVILEGES.append(AD_AC_PR_LINE_2)
ADMIN_ACCOUNT_PRIVILEGES.append(AD_AC_PR_LINE_3)
ADMIN_ACCOUNT_PRIVILEGES.append(AD_AC_PR_LINE_4)
ADMIN_ACCOUNT_PRIVILEGES.append(AD_AC_PR_LINE_5)
#
#
#
#
#
# ----------------------------------------------------------------------------------------------------------------------------------------
#
#
#
#
#
MUFTI_ACCOUNT_PRIVILEGES = []

MUF_ACCOUNT_PR_LINE_1 = LongText(tag='h1', text=_(''))
MUF_ACCOUNT_PR_LINE_2 = LongText(tag='h1', text=_(''))

MUFTI_ACCOUNT_PRIVILEGES.append(MUF_ACCOUNT_PR_LINE_1)
MUFTI_ACCOUNT_PRIVILEGES.append(MUF_ACCOUNT_PR_LINE_2)
#
#
#
#
#
# ----------------------------------------------------------------------------------------------------------------------------------------
#
#
#
#
#
USER_ACCOUNT_PRIVILEGES = []
US_AC_PR_LINE_1 = LongText(tag='h1', text=_(''))
#
#
#
#
#
# ----------------------------------------------------------------------------------------------------------------------------------------
#
#
#
#
#
FAQ_PAGE = []
FAQ_LINE_1 = LongText(tag='h1', text=_('FAQ Page'))
FAQ_PAGE.append(FAQ_LINE_1)
# ect...
# Who are we ? page: briefly
# 	charity/ non profit project
# 	Representation of the founder
# 		name, origin, country, degree, skills and achievements, professional informations (email)
#
# 	Presenting the qa system:
# 		the main feauture of the website (how it was created, used corpus)
#
# 	Motivations:
# 		Master thesis
# 		Religion
# 		introducing islam to the world
# 		spreading religious knowledge among muslims
#
# 	Goals and Ambitions:
# 		Collect a bank of quality fatwas
# 		Respecting the sunni islam charia
# 		Reinforced with prouves from quran and hadith
# 		Creating a community of muslims
# 		Improve the image of Islam and fight islamophobia and misconceptions of muslims in general
#
# 	Future improvements:
# 		new fatwa classes
# 		all plans that were not included before deployment
#
# 	Thesis online view or download *********(and translation)
#
#
# FAQ page:
# 	*The website keep telling me to verify my email, how do i do that ?
# 		make sure you provided a valid email address
# 		check you inbox or spam emails from this address 'fatwa.qas@gmail.com'
# 		then simply click the link and yo're done
# 	*How can i be a mufti in this website ?
# 		requestmuftiform...
# 	*Why am i banned ?
# 		you asked bad questions or volunteered wrong fatwas
# 		you can prove yourself innocent by asking good questions/volunteering good fatwas
#
# Fatwas and qasystem:
# 	even though we trust our users to volunteer fatwas from trusted websites,
# 	a link to the original one is always provided for more inspection
