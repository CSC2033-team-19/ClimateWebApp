# IMPORTS
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import data_required


# challenge form class
class ChallengeForm(FlaskForm):
    title = StringField(validators=[data_required()])
    body = CKEditorField(validators=[data_required()])
    submit = SubmitField()
