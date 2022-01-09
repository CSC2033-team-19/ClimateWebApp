"""
The posts/forms.py module consists of a PostForm class which is used for creating a Flask Form in order to retrieve
information about a Post object.
"""
__author__ = "Inés Ruiz"

# IMPORTS
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import data_required


# post form class
class PostForm(FlaskForm):
    """
    This class represents an instance of a FlaskForm in order to retrieve and save to the database the inputted data
    by user in order to create a Post object.

    Parameters:
        FlaskForm (Form): Flask-specific subclass of WTForms
    """
    title = StringField(validators=[data_required()])
    body = CKEditorField(validators=[data_required()])
    submit = SubmitField()
