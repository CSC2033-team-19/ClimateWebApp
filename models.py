# imports
import base64
import os
from datetime import datetime
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet


# function to encrypt posts
def encrypt(data, key):
    return Fernet(key).encrypt(bytes(data, 'utf-8'))


# function to decrypt posts
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
    donations = db.relationship("Donations")
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
    """
    This class is used to represent the Post object and the 'posts' table in the database.

    Attributes:
        id (Integer): post id, primary key
        email (String): user's email, foreign key with the 'users' table
        created (datetime): date and time of when post was created
        title (Text): post's title
        body (Text): post's body
        image (Text): post's image

    Methods:
        update_post(self, title, body, postkey): encrypts post's title and body
        view_post(self, postkey): decrypts post's title and body
    """
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), db.ForeignKey(User.email), nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False, default=False)
    body = db.Column(db.Text, nullable=False, default=False)
    image = db.Column(db.Text, nullable=False)

    def __init__(self, email, title, body, image, postkey):
        """
        Constructs all the necessary attributes for the post object.

        Parameters:
            email (String): user's email
            title (Text): post's title
            body (Text): post's body
            image (Text): post's image

        Returns:
            Post: object representing a post
        """
        self.email = email
        self.created = datetime.now() # current date and time
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)
        self.image = image
        db.session.commit()

    def update_post(self, title, body, postkey):
        """
        Encrypts post's title and body with the user's postkey and saves the encrypted data to the database.

        Parameters:
            postkey: user's unique encryption key
            title (Text): post's title
            body (Text): post's body

        Returns:
            Post: represents a challenge object with their title and body fields encrypted.
        """
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)
        db.session.commit()

    def view_post(self, postkey):
        """
        Decrypts post's title and body with the user's postkey.

        Parameters:
            postkey: user's unique encryption key

        Returns:
            Post: represents a challenge object with their title and body fields decrypted.
        """
        self.title = decrypt(self.title, postkey)
        self.body = decrypt(self.body, postkey)


# Donation model class
class Donations(db.Model):
    """
     This class is used to represent the Donate object and the 'donations' table in the database.

     Attributes:
         id (Integer): donate id, primary key
         email (String): user's email, foreign key with the 'users' table
         title (Text): charity name or donation title
         created (datetime): date and time of when donation was created
         reason (Text): donation's reason / cause
         donated (Text): total amount donated to the post so far
         amount (Text): the donation goal
         status (Text): either "in progress" or "completed" dependent on if goal is met
         image (Text): image used

     Methods:
         update_donation(self, title, body, postkey): encrypts donation title and body
         view_donation(self, postkey): decrypts donation title and body
     """
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
    """
    This class is used to represent the Challenge object and the 'challenges' table in the database.

    Attributes:
        id (Integer): challenge id, primary key
        email (String): user's email, foreign key with the 'users' table
        created (datetime): date and time of when challenge was created
        title (Text): challenge's title
        body (Text): challenge's body
        image (Text): challenge's image

    Methods:
        update_challenge(self, title, body, postkey): encrypts challenge's title and body
        view_challenge(self, postkey): decrypts challenge's title and body
    """
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), db.ForeignKey(User.email), nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False, default=False)
    body = db.Column(db.Text, nullable=False, default=False)
    image = db.Column(db.Text, nullable=False)

    join_challenge = db.relationship('JoinChallenge')

    def __init__(self, email, title, body, image, postkey):
        """
        Constructs all the necessary attributes for the challenge object.

        Parameters:
            email (String): user's email
            title (Text): challenge's title
            body (Text): challenge's body
            image (Text): challenge's image
            postkey: user's encryption key

        Returns:
            Challenge: object representing a challenge
        """
        self.email = email
        self.created = datetime.now() # current date and time
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)
        self.image = image
        db.session.commit()

    def update_challenge(self, title, body, postkey):
        """
        Encrypts challenge's title and body with the user's postkey and saves the data to the database.

        Parameters:
            postkey: user's unique encryption key
            title (Text): challenge's title
            body (Text): challenge's body

        Returns:
            Challenge: represents a challenge object with their title and body fields encrypted.
        """
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)
        db.session.commit()

    def view_challenge(self, postkey):
        """
        Decrypts challenge's title and body with the user's postkey.

        Parameters:
            postkey: user's unique encryption key

        Returns:
            Challenge: represents a challenge object with their title and body fields decrypted.
        """
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
        self.date_taken = datetime.now()


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
    """
    This class is used to represent the JoinChallenge object and the 'join_challenge' table in the database.

    Attributes:
        id (Integer): join challenge id, primary key
        challenge_id (Integer): challenge id, foreign key with the 'challenges' table
        user_email (String): user's email, foreign key with the 'users' table
        date_joined (datetime): date and time of when the user joined the challenge
    """
    __tablename__ = 'join_challenge'

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey(Challenge.id), nullable=False)
    user_email = db.Column(db.String(100), db.ForeignKey(User.email), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False)

    def __init__(self, challenge_id, email):
        """
        Constructs all the necessary attributes for the join challenge object.

        Parameters:
            challenge_id (Integer): challenge id
            email (String): user's email

        Returns:
            JoinChallenge: object containing the information of when and what challenge a user joined.
        """
        self.challenge_id = challenge_id
        self.user_email = email
        self.date_joined = datetime.now() # current date and time
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

    # create two fake donation posts
    with open(os.path.dirname(__file__) + "/static/images/forest.png", "rb") as img_file:
        image1 = base64.b64encode(img_file.read()).decode('ascii')

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
                                image=image1)
    db.session.add(create_donation)
    db.session.commit()

    with open(os.path.dirname(__file__) + "/static/images/reef.png", "rb") as img_file:
        image2 = base64.b64encode(img_file.read()).decode('ascii')

    create_donation2 = Donations(email='admin@email.com',
                                 title='Coral Reef Alliance',
                                 reason='Their mission: Local, regional, and global levels to keep coral reefs '
                                        'healthy, '
                                        'so they can adapt to climate change and survive for generations to come. As '
                                        'one of the largest global NGOs focused exclusively on protecting coral reefs, '
                                        'the Coral Reef Alliance has used cutting-edge science and '
                                        'engagement for 30 years. '
                                        'Info: https://coral.org/en/',
                                 donated='6,865',
                                 amount='10,000',
                                 status='In progress',
                                 image=image2)
    db.session.add(create_donation2)
    db.session.commit()

    with open(os.path.dirname(__file__) + "/static/images/post1.jpeg", "rb") as img_file:
        post1_image = base64.b64encode(img_file.read()).decode('ascii')

    # create post
    post1 = Post(email='admin@email.com',
                 title='Save energy, save the planet',
                 body='<p>Wasting energy necessitates greater production, and burning fossil fuels is a major source '
                      'of carbon dioxide (CO2), which exacerbates climate change. However, you could start by making '
                      'some simple modifications at home to help and here are some useful tips:</p> '
                      '<p><strong>1.&nbsp; Remove the plug.</strong><br /> When you are not using something, '
                      'switch it off. This includes TVs, DVD players, chargers, speakers, and laptops.</p> '
                      '<p><strong>2.&nbsp; Turn off the lights.</strong><br /> Did you know that lighting can account '
                      'for up to 15% of your energy bill?<br /> You may save energy by turning off lights when not in '
                      'use and using LED energy-efficient light bulbs.</p> <p><strong>3.&nbsp; Conserve '
                      'water.</strong><br /> Purifying and distributing water to our houses consumes a lot of energy, '
                      'therefore conserving water can help reduce greenhouse gas emissions.<br /> You may save money '
                      'by only filling your kettle with what you need and decreasing your water consumption in the '
                      'shower.</p> <p><strong>4.&nbsp; Take charge.</strong><br /> Heating and hot water account for '
                      'more than half of all household energy bills.<br /> So make use of your thermostats, '
                      'controllers, and timers to avoid wasting energy and money.</p> <p><strong>5.&nbsp; Be '
                      'astute.</strong><br /> Check your bill/tariff and make the transition to 100% renewable energy '
                      'sources.<br /> Getting a smart metre will show you how much and what kind of energy you are '
                      'utilising.</p><p><small>Reference: <a '
                      'href="http://www.wwf.org.uk/myfootprint/challenges/save-energy-save-planet-app">Save energy,'
                      'Save the planet | WWF</a></small></p><p><small>Image Reference: <a '
                      'href="https://events.cornell.edu/event/systems_engineering_-_energy_systems_meng_webinar'
                      '">Systems Engineering - Energy Systems M.Eng. Webinar</a></small></p>',
                 image=post1_image,
                 postkey=admin.postkey)

    db.session.add(post1)
    db.session.commit()

    with open(os.path.dirname(__file__) + "/static/images/post2.jpg", "rb") as img_file:
        post2_image = base64.b64encode(img_file.read()).decode('ascii')

    # create post
    post2 = Post(email='admin@email.com',
                 title='Further Causes of Climate Change',
                 body='<p>Climate change is the greenhouse effect of CO₂ (and various other gases) in the atmosphere, '
                      'masking the globe in a huge blanket.</p><p><strong>However, what are the causes of climate '
                      'change?</strong></p><p>Contrary to popular belief, the generation of power is only part of the '
                      'problem.</p><ul><li><strong>Deforestation</strong></li></ul><p>The consistent deforestation '
                      'occurring in our forests and rainforests is also crucial as we are losing a primary source of '
                      'carbon capture (25% of carbon dioxide in the atmosphere is absorbed by trees); the secondary '
                      'effects include the drastic damage to the species that call these habitats their '
                      'home.</p><ul><li><strong>Transport</strong></li></ul><p>Transport is also a huge factor in '
                      'global warming as most transport is powered by internal combustion &ndash; exhaust fumes '
                      'contain toxic gases such as sulphur dioxide and carbon dioxide, which are dispersed into the '
                      'atmosphere despite the best efforts of exhaust catalytic converters.</p><p>There is a slow '
                      'increase in the sale of electric cars but only in recent years has the infrastructure been in '
                      'place to accommodate owning an electric car, in addition, the range of electric cars now '
                      'warrants them being usable on a daily basis.</p><ul><li><strong>Food '
                      'Produce</strong></li></ul><p>Producing food is also a huge factor, for example: the farming of '
                      'cattle is a huge producer of methane, a powerful greenhouse gas. The running of farms and '
                      'processing food uses a lot of energy created from burning fossil fuels &ndash; hence the '
                      'growing cries for everyone to eat locally sourced, vegan, and organic '
                      'produce.</p><p><small>Reference: <a '
                      'href="https://www.un.org/en/climatechange/what-is-climate-change">What is Climate Change? | '
                      'United Nations</a></small></p><p><small>Image Reference: <a '
                      'href="https://www.iberdrola.com/sustainability/against-climate-change">Climate Change | '
                      'Iberdrola</a></small></p>',
                 image=post2_image,
                 postkey=admin.postkey)

    db.session.add(post2)
    db.session.commit()

    with open(os.path.dirname(__file__) + "/static/images/challenge1.png", "rb") as img_file:
        challenge1_image = base64.b64encode(img_file.read()).decode('ascii')

    # create challenge
    challenge1 = Challenge(email='admin@email.com',
                           title='Is your gift wrap recyclable?',
                           body='<p><strong>Our challenge to you:</strong></p><p><strong>Use only recyclable gift '
                                'wrap this holiday season:</strong></p><ul><li>Check for the Forest Stewardship '
                                'Council (FSC) badge, which indicates that the product came from well-managed '
                                'forests.</li><li>Look out for readily available sources online, or consider other '
                                'environmentally friendly alternatives such as reusable wrapping '
                                'fabric.</li></ul><p><strong>Why is out choice of packaging '
                                'important?</strong></p><ul><li>Glitter, foil, laminate, and hazardous dyes are all '
                                'common non-recyclable additives in packaging.</li><li>Sticky tape can&#39;t be '
                                'recycled since it&#39;s too thin or tissue paper has too few fibres.</li><li>The '
                                'vast majority of gift wrap is thrown away.</li></ul><p><strong>How you will make an '
                                'impact?</strong><br />Choose entirely recyclable packaging and make a statement by '
                                'sending an email to paper industries about how sustainability is the future.</p>'
                                '<p><small>Image Reference: <a '
                                'href="https://theeverydayenvironmentalist.com/eco-friendly-gift-wrap/">Eco-friendly '
                                'Gift Wrap</a></small></p>',
                           image=challenge1_image,
                           postkey=admin.postkey)

    db.session.add(challenge1)
    db.session.commit()

    with open(os.path.dirname(__file__) + "/static/images/challenge2.jpeg", "rb") as img_file:
        challenge2_image = base64.b64encode(img_file.read()).decode('ascii')

    # create challenge
    challenge2 = Challenge(email='admin@email.com',
                           title='Sustainable Shopping - Choose a Reusable Bag',
                           body='<p><strong>The challenge:</strong></p><p>At the supermarket or clothing stores use '
                                'reusable bags instead of plastic carrier '
                                'bags.</p><p><strong>Why?</strong></p><p>There&#39;s an easy way to make your '
                                'supermarket or clothes shop more sustainable: at the checkout avoid asking for new '
                                'plastic carrier bags and instead carry your groceries or goods in a reusable '
                                'bag.</p><p><strong>How you will make an impact?</strong></p><p>Plastic carrier bags '
                                'are often only used a handful of times before being thrown away, and for many of us '
                                'they can&#39;t be recycled at home.</p><p>While they may be convenient to use, '
                                'plastic bags take too much time to break down. A plastic bag can take from 15 to 1,'
                                '000 years to break down. In addition, the cost of recycling plastic bags outweighs '
                                'their value.</p><p>Making a switch to a more <strong>sustainable '
                                'alternative</strong> such as bringing a reusable bag from home with you can be the '
                                'smartest move to make, in order to help reduce the impact of plastic bags on the '
                                'environment.</p><p>Plastic pollution kills wildlife, damages natural ecosystems, '
                                'and contributes to climate change. Plastic waste has been found in soils, '
                                'rivers and oceans where it can degrade or destroy wildlife habitats.</p><p>Stand '
                                'against unnecessary plastic production and choose a <strong>reusable bag '
                                '</strong>instead.</p><p><small>Image Reference: <a '
                                'href="https://www.ecofriendlyhabits.com/reusable-grocery-bags/">Eco-friendly '
                                'Reusable Bags</a></small></p>',
                           image=challenge2_image,
                           postkey=admin.postkey)

    db.session.add(challenge2)
    db.session.commit()
