# imports
import base64
from datetime import datetime

from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet


# function to encrypt posts / challenges / card details etc later on TODO
def encrypt(data, key):
    return Fernet(key).encrypt(bytes(data, 'utf-8'))


# function to decrypt posts / challenges / card details etc later on TODO
def decrypt(data, key):
    return Fernet(key).decrypt(data).decode("utf-8")


# Create association table for joining an event
join_event = db.Table("join_event", db.Model.metadata,
                      db.Column("event_id", db.Integer, db.ForeignKey("events.id")),
                      db.Column("user_id", db.Integer, db.ForeignKey("users.id"))
                      )
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
    created_events = db.relationship("Event")
    events = db.relationship('Event', secondary=join_event, back_populates="users")
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

    # image = db.Column(db.Blob)

    def __init__(self, title, email, status, reason, donated, amount):
        self.title = title
        self.status = status
        self.email = email
        self.created = datetime.now()
        self.reason = reason
        self.donated = donated
        self.amount = amount
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


# Event class
class Event(db.Model):
    __tablename__ = "events"

    # Initialise columns of the table
    id = db.Column(db.Integer, primary_key=True)
    head = db.Column(db.String)
    body = db.Column(db.String)
    capacity = db.Column(db.Integer)

    # Time and place
    time = db.Column(db.DateTime)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    address = db.Column(db.String)

    # Created by
    created_by = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    # Create *..* relationship with users
    users = db.relationship("User", secondary=join_event, back_populates="events")

    def __init__(self, head, body, capacity, time, lat, lng, address, created_by):
        self.head = head
        self.body = body
        self.capacity = capacity
        self.time = time
        self.lat = lat
        self.lng = lng
        self.address = address
        self.created_by = created_by

    def update_event(self, head, body, capacity, time, lat, lng, address):
        self.head = head
        self.body = body
        self.capacity = capacity
        self.time = time
        self.lat = lat
        self.lng = lng
        self.address = address
        db.session.commit() 



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

    event_1 = Event(head="Open lecture on climate change",
                    body="Lecture on the long term effects of the warming climate",
                    capacity=100,
                    time=datetime.now().replace(2022, 1, 31, 15, 30),
                    lat=54.9799884,
                    lng=-1.6189398,
                    address="Newcastle University, Newcastle upon Tyne NE1 7RU",
                    created_by=1)

    event_2 = Event(head="Climate conscious discussion forum",
                    body="A place to discuss how to improve your carbon footprint with local experts",
                    capacity=30,
                    time=datetime.now().replace(2022, 1, 22, 12, 0),
                    lat=54.9824472,
                    lng=-1.6113149,
                    address="Philip Robinson Library, Jesmond Rd W, Newcastle upon Tyne NE2 4HQ",
                    created_by=1)

    event_3 = Event(head="Volunteers needed cleaning up the local park",
                    body="Lecture on the long term effects of the warming climate",
                    capacity=100,
                    time=datetime.now().replace(2022, 1, 26, 8, 30),
                    lat=54.990446,
                    lng=-1.6128411,
                    address="Claremont Rd, Newcastle upon Tyne NE2 4PZ",
                    created_by=1)

    event_4 = Event(head="Fundraising event",
                    body="Sustainable event meant to raise awareness on climate issues in a fun way.",
                    capacity=200,
                    time=datetime.now().replace(2022, 2, 28, 12, 0),
                    lat=40.6848898,
                    lng=-74.0759989,
                    address="200 Morris Pesin Drive, Jersey City, NJ 07305, United States",
                    created_by=1
                    )

    db.session.add(event_1)
    db.session.add(event_2)
    db.session.add(event_3)
    db.session.add(event_4)
    db.session.commit()
