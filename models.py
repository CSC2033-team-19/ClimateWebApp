import base64
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.testing import db
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes

# function to encrypt posts / feed / card details etc later on TODO
def encrypt(data, key):
    return Fernet(key).encrypt(bytes(data, 'utf-8'))

# function to decrypt posts / feed / card details etc later on TODO
def decrypt(data, key):
    return Fernet(key).decrypt(data).decode("utf-8")


'''
User Model class for user to save data in
'''


# class User(db.Model, UserMixin):
#     __tablename__ = 'users'
#
#     id = db.Column(db.Integer, primary_key=True)
#     # User authentication information.
#     email = db.Column(db.String(100), nullable=False, unique=True)
#     password = db.Column(db.String(100), nullable=False)
#     pin_key = db.Column(db.String(100), nullable=False)
#
#     # User information
#     firstname = db.Column(db.String(100), nullable=False)
#     lastname = db.Column(db.String(100), nullable=False)
#     phone = db.Column(db.String(100), nullable=False)
#     role = db.Column(db.String(100), nullable=False, default='user')
#
#     # User activity information
#     registered_on = db.Column(db.DateTime, nullable=False)
#     last_logged_in = db.Column(db.DateTime, nullable=True)
#     current_logged_in = db.Column(db.DateTime, nullable=True)
#
#     def __init__(self, email, firstname, lastname, phone, password, pin_key, role):
#         self.email = email
#         self.firstname = firstname
#         self.lastname = lastname
#         self.phone = phone
#         self.password = generate_password_hash(password)
#         self.pin_key = pin_key
#         self.role = role
#         self.registered_on = datetime.now()
#         self.last_logged_in = None
#         self.current_logged_in = None




