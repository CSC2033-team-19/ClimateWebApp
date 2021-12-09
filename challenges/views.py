import copy
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import desc
from app import db, requires_roles
from challenges.forms import ChallengeForm
from models import User, Challenge

# CONFIG
challenges_blueprint = Blueprint('challenges', __name__, template_folder='templates')


@challenges_blueprint.route('/challenges')
@login_required
def challenges():
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

    return render_template('challenges.html', challenges=decrypted_challenges)


@challenges_blueprint.route('/create_challenge', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def create():
    form = ChallengeForm()

    if form.validate_on_submit():
        new_challenge = Challenge(email=current_user.email, title=form.title.data, body=form.body.data, postkey=current_user.postkey)

        db.session.add(new_challenge)
        db.session.commit()

        return challenges()
    return render_template('create_challenge.html', form=form)


@challenges_blueprint.route('/<int:id>/update_challenge', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def update(id):
    challenge = Challenge.query.filter_by(id=id).first()
    if not challenge:
        return render_template('500.html')

    form = ChallengeForm()

    if form.validate_on_submit():
        challenge.update_challenge(form.title.data, form.body.data, current_user.postkey)
        db.session.commit()
        return challenges()

    # creates a copy of challenge object which is independent of database.
    challenge_copy = copy.deepcopy(challenge)

    # decrypt copy of challenge object.
    challenge_copy.view_challenge(current_user.postkey)

    # set update form with title and body of copied challenge object
    form.title.data = challenge_copy.title
    form.body.data = challenge_copy.body

    return render_template('update_challenge.html', form=form)


@challenges_blueprint.route('/<int:id>/delete')
@login_required
@requires_roles('admin')
def delete(id):
    Challenge.query.filter_by(id=id).delete()
    db.session.commit()

    return challenges()
