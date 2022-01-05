# IMPORTS
import logging
import socket
from functools import wraps
import stripe
from flask import Flask, render_template, request, jsonify, redirect
from flask_ckeditor import CKEditor
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv, find_dotenv
import sshtunnel

# Setup Stripe python client library.
from itsdangerous import json
load_dotenv(find_dotenv())

# Ensure environment variables are set.
price = os.getenv('PRICE')
if price is None or price == 'price_12345' or price == '':
    print('You must set a Price ID in .env. Please see the README.')
    exit(0)

# For sample support reference:
stripe.set_app_info(
    'stripe-samples/checkout-one-time-payments',
    version='0.0.1',
    url='https://github.com/stripe-samples/checkout-one-time-payments')

stripe.api_version = '2020-08-27'
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# CONFIG
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://csc2033_team19:SeerMid._Dim@127.0.0.1:{" \
# f"{tunnel.local_bind_port}/csc2033_team19 "
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'

# DB FOR TESTING
app = Flask(__name__)
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///greenify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = "6Leg-5wdAAAAAAs7FQBG-GzvllDhnGUCEAZOpj6C"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6Leg-5wdAAAAAJMdYCe4qxf5xZxt-qmJxGxgyySn"


@app.route('/create-customer', methods=['POST'])
def create_customer():

    """
    This function creates a object representing a customer of for the business (Greenify).
    It lets you create recurring charges and track payments that belong to the same customer on our
    stripe dashboard at https://dashboard.stripe.com
    """

    # Reads application/json and returns a response
    data = json.loads(request.data)
    try:
        # Create a new customer object
        customer = stripe.Customer.create(email=data['email'])

        # Associate the ID of the Customer object with
        # internal representation of a customer.
        resp = jsonify(customer=customer)

        # We're simulating authentication here by storing the ID of the customer
        # in a cookie.
        resp.set_cookie('customer', customer.id)

        return resp
    except Exception as e:
        return jsonify(error=str(e)), 403


# configuration for stripe
@app.route('/config', methods=['GET'])
def get_publishable_key():
    """
    This function makes a AJAX request from the client to the server requesting the publishable key,
    respond with the key and Use the key to create a new instance.
    """

    price = stripe.Price.retrieve(os.getenv('PRICE'))
    return jsonify({
      'publicKey': os.getenv('STRIPE_PUBLISHABLE_KEY'),
      'unitAmount': price['unit_amount'],
      'currency': price['currency']
    })


# Webhook for stripe payment events
@app.route('/webhook', methods=['POST'])
def webhook_received():
    """
    This function configures webhook endpoints via the API to be notified about events that happen the Stripe
    account.

    Return: notifications.
    """

    # Webhooks to receive information about asynchronous payment events.
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    print('event ' + event_type)

    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')

    return jsonify({'status': 'success'})


# FUNCTIONS
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logging.warning('SECURITY - Unauthorised access attempt [%s, %s, %s, %s]',
                                current_user.id,
                                current_user.email,
                                current_user.role,
                                request.remote_addr)
                # Redirect the user to an unauthorised notice!
                return render_template('403.html')
            return f(*args, **kwargs)

        return wrapped

    return wrapper


# LOGGING
class SecurityFilter(logging.Filter):
    def filter(self, record):
        return "SECURITY" in record.getMessage()


# create file handler to log security messages to file
fh = logging.FileHandler(os.path.dirname(__file__) + '/climatewebapp.log', 'w')
fh.setLevel(logging.WARNING)
fh.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
fh.setFormatter(formatter)

# add handler to root logger
logger = logging.getLogger('')
logger.addHandler(fh)
# stop handler messages being sent to root logger
logger.propagate = False


# initialise database
db = SQLAlchemy(app)

# initialise text editor
ckeditor = CKEditor(app)

# security headers TODO


# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('index.html')


# ERROR PAGE VIEWS
@app.errorhandler(400)
def page_forbidden(error):
    return render_template('400.html'), 400


@app.errorhandler(403)
def page_forbidden(error):
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.errorhandler(503)
def page_forbidden(error):
    return render_template('503.html'), 503

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')


if __name__ == '__main__':
    my_host = "127.0.0.1"
    '''
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((my_host, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()
    '''
    # LOGIN MANAGER
    # create instance of LoginManager to hold the settings used for logging in
    login_manager = LoginManager()
    # page users will be redirected to if trying to access a page that they need to be logged in to access
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models import User

    # queries the database and returns the user object which the matching ID
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    # BLUEPRINTS
    # import blueprints
    from users.views import users_blueprint
    from admin.views import admin_blueprint
    from challenges.views import challenges_blueprint
    from posts.views import posts_blueprint
    from calculator.views import calculator_blueprint
    from donate.views import donate_blueprint
    from maps.views import maps_blueprint

    # register blueprints with app
    app.register_blueprint(users_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(challenges_blueprint)
    app.register_blueprint(posts_blueprint)
    app.register_blueprint(calculator_blueprint)
    app.register_blueprint(donate_blueprint)
    app.register_blueprint(maps_blueprint)

    #free_port
    app.run(host=my_host, port=55757, debug=True)
