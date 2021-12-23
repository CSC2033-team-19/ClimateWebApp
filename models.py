# imports
import base64
from datetime import datetime
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet
from donate.forms import DonationForm


# function to encrypt posts / challenges / card details etc later on TODO
def encrypt(data, key):
    return Fernet(key).encrypt(bytes(data, 'utf-8'))


# function to decrypt posts / challenges / card details etc later on TODO
def decrypt(data, key):
    return Fernet(key).decrypt(data).decode("utf-8")


'''
User Model class 
'''


# User model class
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    # crypto key for user's posts and challenges
    postkey = db.Column(db.BLOB)

    # User activity information
    registered_on = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    posts = db.relationship('Post')
    challenges = db.relationship('Challenge')
    carbon_data = db.relationship('CarbonData')
    join_challenge = db.relationship('JoinChallenge')

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


# Post model class
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), db.ForeignKey(User.email), nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False, default=False)
    body = db.Column(db.Text, nullable=False, default=False)

    def __init__(self, email, title, body, postkey):
        self.email = email
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


# Donation model class
class Donations(db.Model):
    __tablename__ = 'donations'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    email = db.Column(db.String(100), db.ForeignKey(User.email), nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.Text, nullable=False, default=False)
    donated = db.Column(db.Integer, nullable=False, default=False)
    amount = db.Column(db.Integer, nullable=False, default=False)
    status = db.Column(db.Text, nullable=False, default="In Progress")
    image = db.Column(db.Text, nullable=False)

    # image = db.Column(db.Blob)

    def __init__(self, title, email, status, reason, donated, amount, image):
        self.title = title
        self.status = status
        self.email = email
        self.created = datetime.now()
        self.reason = reason
        self.donated = donated
        self.amount = amount
        self.image = image
        db.session.commit()

    # update donation
    def update_donation(self, title, reason, donated, amount, status):
        self.title = title
        self.reason = reason
        self.donated = donated
        self.amount = amount
        self.status = status
        db.session.commit()

    # Function to see if the donation is complete
    def add_donation(self, donated):
        self.donated = self.donated + donated
        if self.donated >= self.amount:
            self.status = 'Completed'
        db.session.commit()


# Challenge model class
class Challenge(db.Model):
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), db.ForeignKey(User.email), nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False, default=False)
    body = db.Column(db.Text, nullable=False, default=False)

    join_challenge = db.relationship('JoinChallenge')

    def __init__(self, email, title, body, postkey):
        self.email = email
        self.created = datetime.now()
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)
        db.session.commit()

    def update_challenge(self, title, body, postkey):
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)
        db.session.commit()

    def view_challenge(self, postkey):
        self.title = decrypt(self.title, postkey)
        self.body = decrypt(self.body, postkey)


# Carbon footprint data class
class CarbonData(db.Model):
    __tablename__ = "carbon_footprint_data"

    # Initialise the columns of the table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    total_emissions = db.Column(db.Float, nullable=False)
    travel = db.Column(db.Float, nullable=False)
    home = db.Column(db.Float, nullable=False)
    food = db.Column(db.Float, nullable=False)
    goods = db.Column(db.Float, nullable=False)
    date_taken = db.Column(db.DateTime, nullable=False)

    def __init__(self, user, total, _travel, _home, _food, _goods):
        self.user_id = user.id
        self.total_emissions = total
        self.travel = _travel
        self.home = _home
        self.food = _food
        self.goods = _goods
        self.date_taken = datetime.utcnow()


# Join Challenge model class
class JoinChallenge(db.Model):
    __tablename__ = 'join_challenge'

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey(Challenge.id), nullable=False)
    user_email = db.Column(db.String(100), db.ForeignKey(User.email), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False)

    def __init__(self, challenge_id, email):
        self.challenge_id = challenge_id
        self.user_email = email
        self.date_joined = datetime.now()
        db.session.commit()


# Contact Us model class
class Contact(db.Model):
    __tablename__ = 'contact'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.Text, nullable=False, default=False)
    message = db.Column(db.Text, nullable=False, default=False)
    date = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, email, subject, message):
        self.name = name
        self.email = email
        self.subject = subject
        self.message = message
        self.date = datetime.now()
        db.session.commit()


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

    create_donation = Donations(email='admin@email.com',
                                title='Deforestation, Portel-Pará',
                                reason='Location: Brazil, South America. This Portel-Pará REDD project is working to '
                                       'prevent unplanned deforestation '
                                       'in native forests, which has occurred due to logging, squattering and attempts '
                                       'to implement pastures. '
                                       'Info: https://www.globalclimateinstitute.com/en/portel-para-deforestation-redd/',
                                donated='2000',
                                amount='2000',
                                status='Completed',
                                image="/static/donation.png")
    db.session.add(create_donation)
    db.session.commit()