# Import modules
import os

import flask

from app import db, requires_roles
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import current_user, login_required
import logging
from models import Event

from models import Event, JoinEvent
from maps.forms import EventForm


# Config
maps_blueprint = Blueprint("maps", __name__, template_folder="templates")

# Views
@maps_blueprint.route("/events", methods=["GET"])
@login_required
def events():
    return render_template("maps.html")


@maps_blueprint.route("/events/get_events.json", methods=["GET"])
@login_required
def get_events():
    # Get events from database
    events = Event.query.all()

    # Format the event query into a JSON file to be fetched by the javascript when creating the map.
    event_map = list(map(lambda event: {
        "id": event.id,
        "head": event.head,
        "body": event.body,
        "attending": {"users": JoinEvent.query.with_entities(JoinEvent.user_id).filter_by(event_id=event.id).all()},
        "capacity": event.capacity,
        "time": event.time,
        "address": event.address,
        "lat": event.lat,
        "lng": event.lng
    }, events))

    return jsonify({"key": os.environ["GMAP-KEY"], "events": event_map})

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
