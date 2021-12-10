# IMPORTS
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import data_required


# challenge form class
class ChallengeForm(FlaskForm):
    title = StringField(validators=[data_required()])
    body = TextAreaField(validators=[data_required()])
    submit = SubmitField()
