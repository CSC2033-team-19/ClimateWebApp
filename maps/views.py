# Import modules
import os

import flask
import sqlalchemy

from app import requires_roles, db
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import current_user, login_required
import logging

from models import Event, join_event, User
from maps.forms import EventForm

# Config
maps_blueprint = Blueprint("maps", __name__, template_folder="templates")


# Views
@maps_blueprint.route("/events", methods=["GET"])
@login_required
def events():
    return render_template("maps.html", gmap_key=os.environ["GMAP-KEY"])


@maps_blueprint.route("/events/handle_event", methods=["POST"])
@login_required
def handle_event():
    # Fetch the row related to the user in the event-user association
    event_user = Event.query.filter(Event.users.any(id=current_user.id))

    # Check if row already exists before enlisting the user.
    if event_user.first() is None:
        # Add the user into the event

        event = Event.query.filter_by(id=request.form["event_id"]).first()
        event.users.append(current_user)
        result_string = "User added to event list"


    else:
        # user already in event, so they want to delist from this event.

        deletion = join_event.delete().where(join_event.c.event_id == request.form["event_id"], join_event.c.user_id == current_user.id)

        db.session.execute(deletion)
        result_string = "User removed from event list"

    # Commit changes to the database.
    db.session.commit()

    return jsonify({"result": result_string})


def map_event(event):
    return ({
        "id": event.id,
        "head": event.head,
        "body": event.body,
        "attending": {
            "users": len(event.users),
            "current_user_attending": any(current_user.id == user.id for user in event.users)
        },
        "capacity": event.capacity,
        "time": event.time.strftime("%d/%m/%Y %I:%M %p"),
        "address": event.address,
        "lat": event.lat,
        "lng": event.lng
    })

@maps_blueprint.route("/events/get_events.json", methods=["GET"])
@login_required
def get_events():
    # Get events from database, join with the users table to get their id
    events = Event.query.all()

    # Format the event query into a JSON file to be fetched by the javascript when creating the map.
    prepared_events = list(map(map_event, events))

    return jsonify({"events": prepared_events})


@maps_blueprint.route("/events/create_event", methods=["GET", "POST"])
@login_required
@requires_roles("admin")
def create_event():
    form = EventForm()

    # if form valid
    if form.validate_on_submit():
        # create a new post with the form data
        new_event = Event(
            head=form.head.data,
            body=form.body.data,
            capacity=form.capacity.data,
            time=form.get_date_time(),
            lat=form.lat,
            lng=form.lng,
            address=form.address.data
        )

        print(map_event(new_event))
        # add the new post to the database
        db.session.add(new_event)
        db.session.commit()

        return render_template('create_event.html', form=EventForm())

    # re-render create_post page
    return render_template('create_event.html', form=form)
