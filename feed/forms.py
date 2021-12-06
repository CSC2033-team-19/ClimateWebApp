from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField



class PostForm(FlaskForm):
    title = StringField()
    submit = SubmitField()
