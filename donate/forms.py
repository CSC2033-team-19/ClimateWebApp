from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, FileField
from wtforms.validators import data_required


# post form class
class DonationForm(FlaskForm):
    """
        @author: Oliver Watson

        This class represents an instance of a FlaskForm in order to retrieve and save to the database the inputted data
        by user in order to create a Donation object.

        @param FlaskForm(Form): Flask-specific subclass of WTForms
    """

    title = TextAreaField(validators=[data_required()])
    reason = StringField(validators=[data_required()])
    amount = IntegerField(validators=[data_required()])
    status = TextAreaField()
    submit = SubmitField()
    image = FileField('Update Picture')
