import stripe
from flask import Blueprint, render_template, request
from flask_login import login_required

from app import stripe_keys


# def index():
#     return render_template('donate.html', key=stripe_keys['publishable_key'])
#
#
# charge_blueprint = Blueprint("charge", __name__, template_folder="templates")
#
#
# # Views
# @charge_blueprint.route("/charge", methods=["POST"])
# @login_required
# def charge():
#     # Amount in cents
#     amount = 500
#
#     customer = stripe.Customer.create(
#         email='customer@example.com',
#         source=request.form['stripeToken']
#     )
#
#     charge = stripe.Charge.create(
#         customer=customer.id,
#         amount=amount,
#         currency='usd',
#         description='Flask Charge'
#     )
#
#     return render_template('donate.html', amount=amount)
