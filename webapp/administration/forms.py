from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from flask_babel import _l
from wtforms.validators import DataRequired


class GeneralForm(FlaskForm):
    min_data_per_class = IntegerField(_l('Minimum data per class for a classification training'),
                                      validators=[DataRequired()])
    del_quest_ban = IntegerField(_l('Deleted questions before restricting'),
                                 validators=[DataRequired()])
    del_vol_ban = IntegerField(_l('Deleted vol fatwas before restricting'),
                               validators=[DataRequired()])
    # MIN_QASYSTEM_SIM
    # MAX_DOC_ORDER
    submit = SubmitField(_l('Submit'))
