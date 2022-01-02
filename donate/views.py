import copy
from flask import Blueprint, render_template, jsonify, request, redirect, flash
from flask_login import login_required, current_user
from sqlalchemy import desc
import stripe
from app import db, requires_roles
from donate.forms import DonationForm
from models import Donations
import base64
import os


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

# render picture admin uploads
def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic

# create a new donation
@donate_blueprint.route('/create_donation', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def create():
    form = DonationForm()

    # if form valid
    if form.validate_on_submit():
        file = form.image.data
        data = file.read()
        render_pic = render_picture(data)

        # create a new post with the form data
        new_donation = \
            Donations(title=form.title.data,
                      email=current_user.email,
                      reason=form.reason.data,
                      amount=form.amount.data,
                      donated=0,
                      status=form.status.data,
                      image=render_pic)

        # add the new post to the database
        db.session.add(new_donation)
        db.session.commit()
        return donate()

    # re-render create_post page
    return render_template('create_donation.html', form=form)


# update or edit a donation
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
        donation.update_donation(form.title.data, form.reason.data, form.donated.data, form.amount.data,
                                 form.status.data)
        db.session.commit()
        # send admin to posts page
        return donate()

    # creates a copy of post object which is independent of database
    donation_copy = copy.deepcopy(donation)

    # set update form with title and body of copied post object
    form.title.data = donation_copy.title
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


@donate_blueprint.route('/<int:id>/create-session', methods=['POST'])
@login_required
def create_session(id):
    domain_url = os.getenv('DOMAIN')
    # data = json.loads(request.data)
    donation = Donations.query.filter_by(id=id).first()
    # print(data)
    print(donation.reason)
    amount = request.form['amount']
    session = stripe.checkout.Session.create(
        success_url=domain_url + '/success?id={CHECKOUT_SESSION_ID}',
        cancel_url=domain_url + '/cancel',
        submit_type='donate',
        payment_method_types=['card'],
        line_items=[{
            'amount': amount,
            'name': 'Donation',
            'currency': 'GBP',
            'quantity': 1
        }],
        payment_intent_data={
            'metadata': {
                'cause': donation.reason,
                'donation_by': current_user.email
            },
        },
        metadata={
            'cause': donation.reason,
            'donation_by': current_user.email

        }
    )
    donation.add_donation(int(amount))
    return redirect(session['url'])
3

# retrieving sessions
@donate_blueprint.route('/retrieve_session', methods=['POST'])
@login_required
def retrieve_session():
    session = stripe.checkout.Session.retrieve(
        request.args['id'],
        expand=['payment_intent'],
    )
    return jsonify(session)


