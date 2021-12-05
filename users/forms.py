# IMPORTS
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField


# register form class
class RegisterForm(FlaskForm):
    email = StringField()
    firstname = StringField()
    lastname = StringField()
    phone = StringField()
    password = PasswordField()
    confirm_password = PasswordField()
    submit = SubmitField()


# login form class
class LoginForm(FlaskForm):
    email = StringField()
    password = PasswordField()
    submit = SubmitField()
