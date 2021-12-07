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
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)

    # crypto key for user's posts
    postkey = db.Column(db.BLOB)
    pinkey = db.Column(db.String(100), nullable=False)

    registered_on = db.Column(db.DateTime, nullable=False)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)

    feeds = db.relationship('Post')
    carbon_data = db.relationship("CarbonData")

    def __init__(self, username, password, role, pinkey):
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role
        self.postkey = base64.urlsafe_b64encode(scrypt(password, str(get_random_bytes(32)), 32, N=2 ** 14, r=8, p=1))
        self.pinkey = pinkey
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = None


class CarbonData(db.Model):

    __tablename__ = "carbon_footprint_data"

    # Initialise the columns of the table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, db.ForeignKey(User.username), nullable=False)
    total_emissions = db.Column(db.Float, nullable=False)
    travel = db.Column(db.Float, nullable=False)
    home = db.Column(db.Float, nullable=False)
    food = db.Column(db.Float, nullable=False)
    goods = db.Column(db.Float, nullable=False)
    date_taken = db.Column(db.DateTime, nullable=False)

    def __init__(self, total, _travel, _home, _food, _goods):
        # self.username = current_user.username TODO implement with current_user
        self.total_emissions = total
        self.travel = _travel
        self.home = _home
        self.food = _food
        self.goods = _goods
        self.date_taken = datetime.utcnow().date()


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

    #def init_db():
    #    db.drop_all()
    #    db.create_all()
    #    new_user = User(username='user1@test.com', password='mysecretpassword', role='admin',
    #                    pinkey='BFB5S34STBLZCOB22K6PPYDCMZMH46OJ')
    #    db.session.add(new_user)
    #    db.session.commit()