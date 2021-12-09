# IMPORTS
import logging
from datetime import datetime
import pyotp
from flask import render_template, flash, redirect, url_for, session, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import User
from users.forms import RegisterForm, LoginForm
from app import db

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        # return login()
        user = User.query.filter_by(email=form.email.data).first()

        # if this returns a user, then the email already exists in database

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

        # sends user to login page
        return redirect(url_for('users.login'))
    # if request method is GET or form not valid re-render signup page
    return render_template('register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():

    # if session attribute logins does not exist create attribute logins
    if not session.get('logins'):
        session['logins'] = 0

    # if login attempts is 3 or more create an error message
    elif session.get('logins') >= 3:
        flash('Number of incorrect logins exceeded')

    # create login form object
    form = LoginForm()

    if form.validate_on_submit():

        # increase login attempts by 1
        session['logins'] += 1

        user = User.query.filter_by(email=form.email.data).first()

        if not user or not check_password_hash(user.password, form.password.data):

            # if no match create appropriate error message based on login attempts
            if session['logins'] == 3:
                flash('Number of incorrect logins exceeded')
            elif session['logins'] == 2:
                flash('Please check your login details and try again. 1 login attempt remaining')
            else:
                flash('Please check your login details and try again. 2 login attempts remaining')

            return render_template('login.html', form=form)

        session['logins'] = 0

        login_user(user)
        # direct to role appropriate page
        user.last_logged_in = user.current_logged_in
        user.current_logged_in = datetime.now()
        db.session.add(user)
        db.session.commit()
        logging.info(user.firstname + " has successfully logged in the application")
        if current_user.role == 'admin':
            return redirect(url_for('admin.admin'))
        else:
            return redirect(url_for('users.profile'))

    return render_template('login.html', form=form)


# view user profile
@users_blueprint.route('/profile')
@login_required
def profile():
    return render_template('profile.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone)


@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
