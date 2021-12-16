import copy
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import desc
from app import db, requires_roles
from donate.forms import DonationForm
from models import Donations

# CONFIG
donate_blueprint = Blueprint("donate", __name__, template_folder="templates")


# VIEWS
# view feed homepage
@donate_blueprint.route('/donate')
@login_required
def donate():
    donations = Donations.query.order_by(desc('id')).all()

    # creates a list of copied post objects which are independent of database.
    donation_copy = list(map(lambda x: copy.deepcopy(x), donations))

    return render_template('donate.html', donations=donation_copy)


# create a new donation
@donate_blueprint.route('/create_donation', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def create():
    form = DonationForm()

    # if form valid
    if form.validate_on_submit():
        # create a new post with the form data
        new_donation = Donations(email=current_user.email, reason=form.reason.data, amount=form.amount.data, donated=0)
        # add the new post to the database
        db.session.add(new_donation)
        db.session.commit()
        return donate()

    # re-render create_post page
    return render_template('create_donation.html', form=form)


# update or edit a post
@donate_blueprint.route('/<int:id>/update_donation', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def update(id):
    # get draw with the matching id
    donation = Donations.query.filter_by(id=id).first()

    # if post with given id does not exist
    if not donation:
        # re-render Internal Server Error page
        return render_template('500.html')

    # create Post object
    form = DonationForm()

    # if form valid
    if form.validate_on_submit():
        # update old post data with the new form data and commit it to database
        donation.update_post(form.reason.data, form.amount.data)
        db.session.commit()
        # send admin to posts page
        return donate()

    # creates a copy of post object which is independent of database
    donation_copy = copy.deepcopy(donation)

    # set update form with title and body of copied post object
    form.reason.data = donation_copy.reason
    form.amount.data = donation_copy.amount

    # re-render update_post template
    return render_template('update_donation.html', form=form)


# delete a post
@donate_blueprint.route('/<int:id>/delete')
@login_required
@requires_roles('admin')
def delete(id):
    # delete post which id matches
    Donations.query.filter_by(id=id).delete()
    db.session.commit()
    return donate()
