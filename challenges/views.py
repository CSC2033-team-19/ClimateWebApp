"""
The challenges/views.py module represents the Challenges System functionality and contains all its functions.
"""
__author__ = "Inés Ruiz"

import base64
import copy
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import desc
from app import db, requires_roles
from challenges.forms import ChallengeForm
from models import User, Challenge, JoinChallenge

# CONFIG
challenges_blueprint = Blueprint('challenges', __name__, template_folder='templates')


# VIEWS
# view challenges page
@challenges_blueprint.route('/challenges')
@login_required
def challenges():
    """
    This function retrieves all challenges in descending id order from the database and displays them
    in the challenges.html template.

    Returns:
        render_template('challenges.html', challenges=decrypted_challenges, challenges_for_user=challenge_ids):
            renders the challenges.html template with the decrypted data of each challenge as a variable
            as well as the challenge's id the current user has joined .
    """
    # get all challenges in descending ordered depending on their id number
    challenges = Challenge.query.order_by(desc('id')).all()

    # creates a list of copied post objects which are independent of database.
    challenge_copies = list(map(lambda x: copy.deepcopy(x), challenges))

    # empty list for decrypted copied post objects
    decrypted_challenges = []

    # Create list of challenges which the user is in
    user_challenges = JoinChallenge.query.with_entities(JoinChallenge.challenge_id).filter_by(
        user_email=current_user.email).all()
    challenge_ids = [challenge.challenge_id for challenge in user_challenges]

    # decrypt each copied challenge object and add it to decrypted_challenges array.
    for c in challenge_copies:
        user = User.query.filter_by(email=c.email).first()
        c.view_challenge(user.postkey)
        decrypted_challenges.append(c)

    # re-render challenges page with the decrypted challenges
    return render_template('challenges.html', challenges=decrypted_challenges, challenges_for_user=challenge_ids)


# view individual post
@challenges_blueprint.route('/<int:id>/challenges')
@login_required
def challenge(id):
    """
    This function retrieves the challenge with the matching id from the database and displays it
    in the challenge.html template.

    Parameters:
        id (int): challenge id

    Returns:
        render_template('challenge.html', challenge=challenge_copy, user_in_challenge=user_in_challenge):
            renders the challenge.html template with the decrypted data of the
            matching post id and user_in_challenge as variables.
    """
    # get all posts in descending ordered depending on their id number
    challenge = Challenge.query.get_or_404(id)

    # create post copy
    challenge_copy = copy.deepcopy(challenge)

    # decrypt copy of the current_winning_draw
    user = User.query.filter_by(email=challenge.email).first()
    challenge_copy.view_challenge(user.postkey)

    # Check if user is in the challenge
    user_in_challenge = current_user.email in [user.user_email for user in challenge.join_challenge]

    # re-render posts page with the decrypted posts
    return render_template('challenge.html', challenge=challenge_copy, user_in_challenge=user_in_challenge)


# render picture admin uploads
def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic


# create a new challenge
@challenges_blueprint.route('/create_challenge', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def create():
    """
     This function enables the user with 'admin' role to create a Challenge object
     by retrieving and storing the user input through the ChallengeForm to the database.

     Returns:
         redirect(url_for('challenges.challenge', id=new_challenge.id)): If ChallengeForm valid, it redirects the user
            to the 'challenge' function and passing the challenge id as a variable where the inputted challenge
            data is stored.
         render_template('create_challenge.html', form=form): If ChallengeForm not valid, it re-renders the
            create_challenge template along with the form.
     """
    form = ChallengeForm()

    # if form valid
    if form.validate_on_submit():
        # retrieve input file
        file = request.files['inputFile']
        data = file.read()
        render_file = render_picture(data)

        # create new challenge with the form data
        new_challenge = Challenge(email=current_user.email,
                                  title=form.title.data,
                                  body=form.body.data,
                                  image=render_file,
                                  postkey=current_user.postkey)

        # add new challenge to the database
        db.session.add(new_challenge)
        db.session.commit()

        flash("Challenge Created Successfully")
        return redirect(url_for('challenges.challenge', id=new_challenge.id))

    # re-render create_challenge page
    return render_template('create_challenge.html', form=form)


# update or edit a challenge
@challenges_blueprint.route('/<int:id>/update_challenge', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def update(id):
    """
    This function enables the user with 'admin' role to edit a Challenge object
    by retrieving and storing the new data inputted through the ChallengeForm to the database.

    Parameters:
        id (int): challenge id

    Returns:
        return render_template('500.html'): If no challenge exists with the given id, render 500.html error page.
        return redirect(url_for('challenges.challenge', id=challenge.id)): If ChallengeForm is valid, it redirects the
            user to the 'challenge' function and passing the challenge id as a variable where the new data is stored.
        return render_template('update_challenge.html', form=form): If ChallengeForm not valid, it re-renders
            the update_challenge template along with the form.
    """
    # get challenge with the matching id
    challenge = Challenge.query.filter_by(id=id).first()

    # if challenge with given id does not exist
    if not challenge:
        # re-render Internal Server Error page
        return render_template('500.html')

    # create new Challenge form
    form = ChallengeForm()

    # if form valid
    if form.validate_on_submit():
        # update old challenge data with the new form data and commit changes to database
        challenge.update_challenge(form.title.data, form.body.data, current_user.postkey)
        db.session.commit()
        flash("Challenge Updated Successfully")
        return redirect(url_for('challenges.challenge', id=challenge.id))

    # creates a copy of challenge object which is independent of database.
    challenge_copy = copy.deepcopy(challenge)

    # decrypt copy of challenge object.
    challenge_copy.view_challenge(current_user.postkey)

    # set update form with title and body of copied challenge object
    form.title.data = challenge_copy.title
    form.body.data = challenge_copy.body

    # re-render update_challenge template
    return render_template('update_challenge.html', form=form)


# delete a challenge
@challenges_blueprint.route('/<int:id>/delete_challenge')
@login_required
@requires_roles('admin')
def delete(id):
    """
    This function enables the user with 'admin' role to delete the Challenge object from the database
    which the matches challenge id passed in as a parameter.

    Parameters:
        id (int): challenge id

    Returns:
        challenges(): function which renders the challenges.html template
    """
    # delete challenge which matches id
    Challenge.query.filter_by(id=id).delete()
    db.session.commit()
    flash("Challenge Deleted")
    return challenges()


# join a challenge
@challenges_blueprint.route('/<int:id>/join_challenge', methods=('GET', 'POST'))
@login_required
@requires_roles('user')
def join(id):
    """
    This function enables the user with 'user' role to join a Challenge object by creating a new JoinChallenge
    object with challenge id and the current user email which will be saved to the database.

    Parameters:
        id (int): challenge id

    Returns:
        redirect(url_for('challenges.challenge', id=challenge.id)): redirects user to the 'challenge' function
            with the challenge id that the user will join as a variable.
    """
    # get challenge with the matching id
    challenge = Challenge.query.filter_by(id=id).first()
    # create a new row with the data
    new_join = JoinChallenge(challenge_id=challenge.id, email=current_user.email)

    db.session.add(new_join)
    db.session.commit()

    flash('Challenge Joined Successfully')
    return redirect(url_for('challenges.challenge', id=challenge.id))


# leave a challenge
@challenges_blueprint.route('/<int:id>/leave_challenge', methods=('GET', 'POST'))
@login_required
@requires_roles('user')
def leave(id):
    """
    This function enables the user with 'user' role to leave a Challenge by deleting the existing JoinChallenge object
    from the database, which matches the challenge id passed in as a parameter and the current user email.

    Parameters:
        id (int): challenge id

    Returns:
        redirect(url_for('challenges.challenge', id=challenge.id)): redirects user to the 'challenge' function
            with the challenge id that the user will leave as a variable.
    """
    # get challenge with the matching id
    challenge = Challenge.query.filter_by(id=id).first()

    # delete join_challenge row which matching id
    JoinChallenge.query.filter_by(challenge_id=id, user_email=current_user.email).delete()
    db.session.commit()

    flash("Challenge Left")
    return redirect(url_for('challenges.challenge', id=challenge.id))
