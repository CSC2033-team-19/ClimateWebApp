# IMPORTS
import re
import phonenumbers
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Email, ValidationError, Length, EqualTo


# function that checks for forbidden characters
def character_check(form, field):
    excluded_chars = "*?!'^+%&/()=}][{$#@<>1234567890"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(
                f"Character {char} is not allowed.")


# register form class
class RegisterForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    firstname = StringField(validators=[InputRequired(), character_check])
    lastname = StringField(validators=[InputRequired(), character_check])
    phone = StringField(validators=[InputRequired()])  # TODO add country code selection
    password = PasswordField(
        validators=[InputRequired(),
                    Length(min=6, max=12, message="Password must be between 6 and 12 characters in length.")])
    confirm_password = PasswordField(validators=[InputRequired(),
                                                 EqualTo('password', message="Both password fields must be equal.")])
    submit = SubmitField()




    def validate_password(self, password):

        p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*\W)')
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit, "
                                  "1 lowercase, 1 uppercase and 1 special character.")

    def validate_phone(self, phone):

        try:
            if not (phonenumbers.is_valid_number(phonenumbers.parse(self.phone.data))):
                raise ValidationError("Please enter a valid phone number including country code")

        except:
            raise ValidationError('Please enter a valid phone number including country code')

# login form class
class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired()])
    submit = SubmitField()
