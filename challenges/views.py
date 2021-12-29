import copy
from flask import Blueprint, render_template, flash
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
    # get all challenges in descending ordered depending on their id number
    challenges = Challenge.query.order_by(desc('id')).all()

    # creates a list of copied post objects which are independent of database.
    challenge_copies = list(map(lambda x: copy.deepcopy(x), challenges))

    # empty list for decrypted copied post objects
    decrypted_challenges = []

    # decrypt each copied challenge object and add it to decrypted_challenges array.
    for c in challenge_copies:
        user = User.query.filter_by(email=c.email).first()
        c.view_challenge(user.postkey)
        decrypted_challenges.append(c)

    # re-render challenges page with the decrypted challenges
    return render_template('challenges.html', challenges=decrypted_challenges)


# create a new challenge
@challenges_blueprint.route('/create_challenge', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def create():
    form = ChallengeForm()

    # if form valid
    if form.validate_on_submit():

        # create new challenge with the form data
        new_challenge = Challenge(email=current_user.email, title=form.title.data, body=form.body.data, postkey=current_user.postkey)

        # add new challenge to the database
        db.session.add(new_challenge)
        db.session.commit()

        flash("Challenge Submitted Successfully")
        return challenges()

    # re-render create_challenge page
    return render_template('create_challenge.html', form=form)


# update or edit a challenge
@challenges_blueprint.route('/<int:id>/update_challenge', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def update(id):
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
        return challenges()

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
    # delete challenge which matches id
    Challenge.query.filter_by(id=id).delete()
    db.session.commit()

    return challenges()


# join a challenge
@challenges_blueprint.route('/<int:id>/join_challenge', methods=('GET', 'POST'))
@login_required
@requires_roles('user')
def join(id):
    # get challenge with the matching id
    challenge = Challenge.query.filter_by(id=id).first()
    # create a new row with the data
    new_join = JoinChallenge(challenge_id=challenge.id, email=current_user.email)

    db.session.add(new_join)
    db.session.commit()

    flash('Joined Challenge')

    return challenges()

