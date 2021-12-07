# imports
import base64
from datetime import datetime
from hashlib import scrypt
from Crypto.Random import get_random_bytes
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet


# function to encrypt posts / feed / card details etc later on TODO
def encrypt(data, key):
    return Fernet(key).encrypt(bytes(data, 'utf-8'))


# function to decrypt posts / feed / card details etc later on TODO
def decrypt(data, key):
    return Fernet(key).decrypt(data).decode("utf-8")


'''
User Model class 
'''


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    # User activity information
    registered_on = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    feeds = db.relationship('Post')

    def __init__(self, email, firstname, lastname, phone, password, role):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = generate_password_hash(password)
        self.role = role
        self.postkey = base64.urlsafe_b64encode(scrypt(password, str(get_random_bytes(32)), 32, N=2 ** 14, r=8, p=1))
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = None


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey(User.username), nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False, default=False)
    body = db.Column(db.Text, nullable=False, default=False)

    def __init__(self, username, title, body, postkey):
        self.username = username
        self.created = datetime.now()
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)
        db.session.commit()

    def update_post(self, title, body, postkey):
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)
        db.session.commit()

    def view_post(self, postkey):
        self.title = decrypt(self.title, postkey)
        self.body = decrypt(self.body, postkey)


def init_db():
    db.drop_all()
    db.create_all()
    admin = User(email='admin@email.com',
                 password='Admin1!',
                 firstname='Alice',
                 lastname='Jones',
                 phone='0191-123-4567',
                 role='admin')

    db.session.add(admin)
    db.session.commit()