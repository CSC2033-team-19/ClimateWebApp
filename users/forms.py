# IMPORTS
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Email, ValidationError, Length, EqualTo


# register form class
class RegisterForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    firstname = StringField(validators=[InputRequired()])  # TODO character_check function
    lastname = StringField(validators=[InputRequired()])
    phone = StringField(validators=[InputRequired()])  # TODO phone number validation
    password = PasswordField(  # TODO character validation
        validators=[InputRequired(),
                    Length(min=6, max=12, message="Password must be between 6 and 12 characters in length.")])
    confirm_password = PasswordField(validators=[InputRequired(),
                                                 EqualTo('password', message="Both password fields must be equal.")])
    submit = SubmitField()


# login form class
class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired()])
    submit = SubmitField()
