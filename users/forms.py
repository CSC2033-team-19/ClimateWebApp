# IMPORTS
import re
import phonenumbers
from flask import session
from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Email, ValidationError, Length, EqualTo, Optional


# checks that the input field does not contain the following special characters: *?!'^+%&/()=}][{$#@<>1234567890
def character_check(form, field):
    excluded_chars = "*?!'^+%&/()=}][{$#@<>1234567890"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(
                f"Character {char} is not allowed.")


# checks that the password contains at least 1 digit, 1 lowercase, 1 uppercase and 1 special character
def validate_password(self, password):
    p = re.compile(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)')
    if not p.match(self.password.data):
        raise ValidationError("Password must contain at least 1 digit, 1 lowercase, 1 uppercase and 1 special "
                              "character.")


# checks that the inputted phone number is valid
def validate_phone(self, phone):
    try:
        if not (phonenumbers.is_valid_number(phonenumbers.parse(self.phone.data))):
            raise ValidationError("Please enter a valid phone number including country code")

    except:
        raise ValidationError('Please enter a valid phone number including country code')


# custom validator that makes captcha required after 3 incorrect login attempts
class RequiredIf(Recaptcha, Optional):

    def __call__(self, form, field):

        if session['logins'] < 3:
            Optional().__call__(form, field)
        else:
            Recaptcha().__call__(form, field)


# register form class
class RegisterForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    firstname = StringField(validators=[InputRequired(), character_check])
    lastname = StringField(validators=[InputRequired(), character_check])
    phone = StringField(validators=[InputRequired(), validate_phone])  # TODO add country code selection
    password = PasswordField(
        validators=[InputRequired(), validate_password,
                    Length(min=8, message="Password must be at least 8 characters in length.")])
    confirm_password = PasswordField(validators=[InputRequired(),
                                                 EqualTo('password', message="Both password fields must be equal.")])
    submit = SubmitField()


# login form class
class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired()])
    recaptcha = RecaptchaField(validators=[RequiredIf()])
    submit = SubmitField()
