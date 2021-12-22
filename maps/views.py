# Import modules
import flask

from app import db, requires_roles
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import current_user, login_required
import logging
from models import Event
from flask_googlemaps import Map

from models import Event
from maps.forms import EventForm


# Config
maps_blueprint = Blueprint("maps", __name__, template_folder="templates")

# Views
@maps_blueprint.route("/events", methods=["GET"])
@login_required
def events():
    # Create map in view
    events = Event.query.all()

    return render_template("maps.html")


@maps_blueprint.route('/create_event', methods=('GET', 'POST'))
@login_required
@requires_roles('admin')
def create():
    form = EventForm()

    # if form valid
    if form.validate_on_submit():
        # create a new post with the form data
        new_event = Event(
            head=form.head.data,
            body=form.body.data,
            capacity=form.capacity.data,
            time=form.get_date_time(),
            lat=form.lat,  # Gotten during verification of data
            lng=form.lng,
            address=form.address.data
        )

        # add the new post to the database
        db.session.add(new_event)
        db.session.commit()

        return events()

    # re-render create_post page
    return render_template('create_event.html', form=form)
