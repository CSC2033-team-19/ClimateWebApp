# IMPORTS
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import data_required


# challenge form class
class ChallengeForm(FlaskForm):
    """
    This class represents an instance of a FlaskForm in order to retrieve and save to the database the inputted data
        by user in order to create a Challenge object.

    Parameters:
        FlaskForm(Form): Flask-specific subclass of WTForms
    """
    title = StringField(validators=[data_required()])
    body = CKEditorField(validators=[data_required()])
    submit = SubmitField()
