from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField,SubmitField, TextAreaField
from wtforms.validators import data_required


# post form class
class DonationForm(FlaskForm):
    reason = StringField(validators=[data_required()])
    amount = IntegerField(validators=[data_required()])
    submit = SubmitField()