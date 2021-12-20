# IMPORTS
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import data_required


# post form class
class PostForm(FlaskForm):
    title = StringField(validators=[data_required()])
    body = TextAreaField(validators=[data_required()])
    submit = SubmitField()
