# IMPORTS
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import data_required


# post form class
class PostForm(FlaskForm):
    title = StringField(validators=[data_required()])
    body = CKEditorField(validators=[data_required()])
    submit = SubmitField()
