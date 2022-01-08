# IMPORTS
import re
import phonenumbers
from flask import session
from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, ValidationError, Length, EqualTo, Optional, data_required


def character_check(form, field):
    """
    Checks that the input field does not contain the following special characters: *?!'^+%&/()=}][{$#@<>1234567890
    """
    excluded_chars = "*?!'^+%&/()=}][{$#@<>1234567890"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(
                f"Character {char} is not allowed.")


def validate_password(self, password):
    """
    Checks that the password contains at least 1 digit, 1 lowercase, 1 uppercase and 1 special character
    """
    p = re.compile(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)')
    if not p.match(self.password.data):
        raise ValidationError("Password must contain at least 1 digit, 1 lowercase, 1 uppercase and 1 special "
                              "character.")



def validate_phone(self, phone):
    """
    Checks that the inputted phone number is valid
    """
    try:
        if not (phonenumbers.is_valid_number(phonenumbers.parse(self.phone.data))):
            raise ValidationError("Please enter a valid phone number including country code.")

    except:
        raise ValidationError('Please enter a valid phone number including country code.')


class RequiredIf(Recaptcha, Optional):
    """
    Custom validator that makes captcha required after 3 incorrect login attempts

    @param Recaptcha: Validator, validates a Recaptcha
    @param Optional: Validator, allows empty input

    """


    def __call__(self, form, field):

        if session['logins'] < 3:
            Optional().__call__(form, field)
        else:
            Recaptcha().__call__(form, field)


# register form class
class RegisterForm(FlaskForm):
    """
    This class represents an instance of a FlaskForm in order to retrieve and save to the database the inputted data
    by user in order to create a User object.

    @param FlaskForm(Form): Flask-specific subclass of WTForms
    """

    email = StringField(validators=[InputRequired(), Email()])
    firstname = StringField(validators=[InputRequired(), character_check])
    lastname = StringField(validators=[InputRequired(), character_check])
    phone = StringField(validators=[InputRequired(), validate_phone])
    password = PasswordField(
        validators=[InputRequired(), validate_password,
                    Length(min=8, message="Password must be at least 8 characters in length.")])
    confirm_password = PasswordField(validators=[InputRequired(),
                                                 EqualTo('password', message="Both password fields must be equal.")])
    submit = SubmitField()


# login form class
class LoginForm(FlaskForm):
    """
    Represents a form for the user to enter their login details

    @param FlaskForm(Form): Flask-specific subclass of WTForms
    """
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired()])
    recaptcha = RecaptchaField(validators=[RequiredIf()])
    submit = SubmitField()


# contact form class
class ContactForm(FlaskForm):
    """
    Represents a form for the user to submit inquiries

    @param FlaskForm(Form): Flask-specific subclass of WTForms
    """
    name = StringField(validators=[InputRequired()])
    email = StringField(validators=[InputRequired(), Email()])
    subject = TextAreaField(validators=[InputRequired()])
    message = TextAreaField(validators=[InputRequired()])
    submit = SubmitField()
