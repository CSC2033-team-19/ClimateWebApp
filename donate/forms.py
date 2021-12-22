from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, FileField
from wtforms.validators import data_required


# post form class
class DonationForm(FlaskForm):
    title = TextAreaField(validators=[data_required()])
    reason = StringField(validators=[data_required()])
    amount = IntegerField(validators=[data_required()])
    status = TextAreaField()
    submit = SubmitField()
    image = FileField('Update Picture')