""""
This module contains methods that handle rendering the registration, login, logout, profile and contact pages
"""

__author__ = "Michalina Kazmierczak, Inés Ruiz"

# IMPORTS
import logging
from datetime import datetime
from flask import render_template, flash, redirect, url_for, session, Blueprint, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import User, JoinChallenge, Contact
from users.forms import RegisterForm, LoginForm, ContactForm
from app import index
from app import db

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """
    This function renders the register form and handles input from the form.
    """

    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():

        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(email=form.email.data).first()

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # logging call for when users register
        logging.warning('SECURITY - User registration [%s, %s]', form.email.data, request.remote_addr)

        # sends user to login page
        return redirect(url_for('users.login'))

    # if request method is GET or form not valid re-render signup page
    return render_template('register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    This function renders the login form and handles input from the form.
    """

    # if session attribute logins does not exist create attribute logins
    if not session.get('logins'):
        session['logins'] = 0

    # if login attempts is 6 or more create an error message
    elif session.get('logins') >= 6:
        flash('Number of incorrect logins exceeded')

    # create login form object
    form = LoginForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():

        # increase login attempts by 1
        session['logins'] += 1

        user = User.query.filter_by(email=form.email.data).first()

        # if username does not exist in the database or if username exists but stored password does not match
        if not user or not check_password_hash(user.password, form.password.data):

            # if no match create appropriate error message based on login attempts
            # if login attempt equals 6 create error message
            if session['logins'] == 6:
                flash('Number of incorrect logins exceeded')

                # logging call for when users exceeded login attempts
                logging.warning('SECURITY - Invalid Logins Attempts Exceeded [%s, %s]', form.email.data,
                                request.remote_addr)

            # if login attempt is between 1 and 5 create error message
            else:
                flash('Please check your login details and try again. '
                      '{} login attempt(s) remaining'.format(6 - session['logins']))

                # logging call for when user login info is invalid
                logging.warning('SECURITY - Invalid Login Attempt {} [%s, %s]'.format(session['logins']),
                                form.email.data, request.remote_addr)

            # re-render login page
            return render_template('login.html', form=form)

        # if user exists in database and matches the stored password
        else:

            # if user is verified reset login attempts to 0
            session['logins'] = 0

            # if username and password are both correct, register the user as logged in
            login_user(user)

            # update user activity information in the database
            user.last_logged_in = user.current_logged_in
            user.current_logged_in = datetime.now()
            db.session.add(user)
            db.session.commit()

            # logging call for when users log in
            logging.warning('SECURITY - Log in [%s, %s, %s]', current_user.id, current_user.email,
                            request.remote_addr)

            # direct to role appropriate page
            if current_user.role == 'admin':
                return redirect(url_for('admin.admin'))
            else:
                return redirect(url_for('users.profile'))

    return render_template('login.html', form=form)


# view user profile
@users_blueprint.route('/profile')
@login_required
def profile():
    """
    This function renders the user profile
    """
    return render_template('profile.html',
                           name=current_user.firstname,
                           id=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone)


# view all challenges joined by current user
@users_blueprint.route('/view_joined_challenges', methods=['POST'])
@login_required
def view_joined_challenges():
    """
    This function renders all challenges joined by the current user
    """
    return render_template('profile.html', name=current_user.firstname,
                           id=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone,
                           joined_challenges=JoinChallenge.query.filter_by(user_email=current_user.email))


# view user logout
@users_blueprint.route('/logout')
@login_required
def logout():
    """
    Function for logging users out
    """

    # logging call for when users log out
    logging.warning('SECURITY - Log out [%s, %s, %s]', current_user.id, current_user.email, request.remote_addr)

    logout_user()

    # redirect to home page
    return redirect(url_for('index'))


# view contact us
@users_blueprint.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    This function renders the contact form and handles input from the form.
    """

    form = ContactForm()

    if form.validate_on_submit():

        flash('Form sent')

        # create a new row with the contact form data
        new_contact = Contact(name=form.name.data, email=form.email.data, subject=form.subject.data, message=form.message.data)

        # add the new post to the database
        db.session.add(new_contact)
        db.session.commit()

        return index()

    return render_template('contact.html', form=form)
