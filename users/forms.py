import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email, Length, EqualTo, ValidationError, Regexp

# Login form page UI credentials
class LoginForm(FlaskForm):
    email = StringField(validators=[Required(), Email()])
    password = PasswordField(validators=[Required()])
    pin_key = StringField(validators=[Required()])
    submit = SubmitField()

# character check for register form, raise an error if they're inputted
class RegisterForm(FlaskForm):
    def character_check(self, field):
        excluded_chars = "*?'*?!\'^+$%&/()=\{\}[]$#@<>"
        for char in field.data:
            if char in excluded_chars:
                raise ValidationError(f"Character {char} is not allowed.")

# validate the password by making sure they are the same plus include certain letters / numbers
    def validate_password(self, field):
        p = re.compile(r"(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[a-z])")
        if not p.match(field.data):
            raise ValidationError(
                "Password must contain at least 1 digit, 1 uppercase letter, 1 lowercase letter and 1 special "
                "character. "
            )
# series of other validation forms for each requirement
    email = StringField(validators=[Required(), Email()])
    firstname = StringField(validators=[Required(), character_check])
    lastname = StringField(validators=[Required(), character_check, ])
    phone = StringField(validators=[Required(), Regexp(r'\d{4}-\d{3}-\d{4}', message="Phone must be of the form "
                                                                                     "XXXX-XXX-XXXX")])

    password = PasswordField(validators=[Required(), Length(min=6, max=12, message="Password must be between 6 and 12 "
                                                                                   "characters in length.", ),
                                         validate_password])
    confirm_password = PasswordField(validators=[Required(), EqualTo("password", message="Both password fields must be "
                                                                                         "equal!"), ])
    pin_key = StringField(validators=[Required(), character_check, Length(max=32, min=32, message="Length of PIN key "
                                                                                                  "must be 32.")])
    submit = SubmitField()