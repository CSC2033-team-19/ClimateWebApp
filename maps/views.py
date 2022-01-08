# Import modules
import os
from datetime import datetime

import flask
import sqlalchemy

from app import requires_roles, db
from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect
from flask_login import current_user, login_required
import logging

from models import Event, join_event, User
from maps.forms import EventForm

# Config
maps_blueprint = Blueprint("maps", __name__, template_folder="templates")


# Change database into easily usable JSON file
def map_event(event):
    """
    Map each database row into a JSON element

    Keyword arguments:
    event -- a row in the Event table.
    """
    # Check if event is in the future
    if event.time > datetime.now():
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
            "lng": event.lng,
            "created_by_user": event.created_by == current_user.id
        })
    else:
        # Event has already occurred, pass
        pass


# Views
@maps_blueprint.route("/events/", methods=["GET"])
@login_required
def events():
    """
    Render the events page in the default view
    """
    return render_template("maps.html", gmap_key=os.environ["GMAP-KEY"], focus_event=False)


@maps_blueprint.route("/events/<int:id>", methods=["GET"])
@login_required
def event_id(id):
    """
    Render the events page and focus on a specific event

    Keyword arguments:
    id -- The id which should be focused.
    """
    return render_template("maps.html", gmap_key=os.environ["GMAP-KEY"], focus_event=id)


@maps_blueprint.route("/events/handle_event", methods=["POST"])
@login_required
def handle_event():
    """
    Handle a user trying to join or leave an event.
    """
    # Fetch the row related to the user in the event-user association
    event_user = Event.query.filter(Event.users.any(id=current_user.id), Event.id == request.form["event_id"])

    # Check if row already exists before enlisting the user.
    if event_user.first() is None:
        # Add the user into the event
        event = Event.query.filter_by(id=request.form["event_id"]).first()
        event.users.append(current_user)
        result_string = "User added to event list"


    else:
        # user already in event, so they want to delist from this event.

        deletion = join_event.delete().where(join_event.c.event_id == request.form["event_id"],
                                             join_event.c.user_id == current_user.id)

        db.session.execute(deletion)
        result_string = "User removed from event list"

    # Commit changes to the database.
    db.session.commit()

    return jsonify({"result": result_string, "redirect_to": f"/events/{request.form['event_id']}"})


@maps_blueprint.route("/events/get_events.json", methods=["GET"])
@login_required
def get_events():
    events = Event.query.filter(
                                # Check if the user created the event
                                (Event.created_by == current_user.id)
                                # Check if the user is in the event
                                | (Event.users.any(id=current_user.id))
    )
    if events.first() is None:
        return jsonify({"success": False})
    events = events.all()

    # Format the event query into a JSON file to be fetched by the javascript when creating the map.
    prepared_events = list(map(map_event, events))

    return jsonify({"events": prepared_events, "success": True})


@maps_blueprint.route("/events/get_local_events.json", methods=["GET"])
@login_required
def get_local_events():
    """
    Get all events within a certain radius of the user.
    """
    # Distance
    radius = 1

    # Get events from the database that are within {radius} of the user at the time.
    events = Event.query.filter(
                                # Check if the event is within 50km of the user's location (latitude)
                                (Event.lat < (float(request.args["lat"]) + radius))
                                & (Event.lat > (float(request.args["lat"]) - radius))
                                # Check if the event is within 50km of the user's location (longitude)
                                & (Event.lng < (float(request.args["lng"]) + radius))
                                & (Event.lng > (float(request.args["lng"]) - radius))
                                )

    if events.first() is None:
        return jsonify({"success": False})

    events = events.all()
    # Format the event query into a JSON file to be fetched by the javascript when creating the map.
    prepared_events = list(map(map_event, events))


    return jsonify({"events": prepared_events, "success": True})


@maps_blueprint.route("/events/event_details.json")
@login_required
def get_event():
    """
    Get an event with a specific ID.
    """
    # Get event
    event = Event.query.filter(Event.id == request.args["id"]).first()

    # Format event
    return_object = map_event(event)

    # Check if null
    if return_object is None:
        return jsonify({"success": False})

    # Return result.
    return jsonify({"success": True, "result": return_object})


@maps_blueprint.route("/events/create_event", methods=["GET", "POST"])
@login_required
@requires_roles("admin")
def create_event():
    """
    Render the create event form and handle input from the form.
    """
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
            address=form.address.data,
            created_by=current_user.id
        )

        # add the new post to the database
        db.session.add(new_event)
        db.session.commit()

        return render_template('create_event.html', form=EventForm())

    # re-render create_post page
    return render_template('create_event.html', form=form)


@maps_blueprint.route("/events/update_event/<int:id>", methods=["GET", "POST"])
@login_required
@requires_roles("admin")
def update_event(id):
    """
    Render the update event form for a specific ID, and handle input from the form.

    Keyword arguments:
    id -- The id of the event which is being updated.
    """
    # get event with the matching id
    event = Event.query.filter_by(id=id).first()

    # if event with given id does not exist
    if not event:
        return render_template("500.html")

    # Create new event form
    form = EventForm()

    # if form valid
    if form.validate_on_submit():
        # update old event data with new data
        time = form.get_date_time()

        event.update_event(form.head.data,
                           form.body.data,
                           form.capacity.data,
                           time,
                           form.lat,
                           form.lng,
                           form.address.data)
        db.session.commit()
        return event_id(id)

    # Fill out form with event data
    form.fill_data(event)

    # render update_challenge template
    return render_template("update_event.html", form=form)


@maps_blueprint.route("/events/delete_event/<int:id>", methods=["GET", "POST"])
@login_required
@requires_roles("admin")
def delete_event(id):
    """
    Delete an event with a given id

    Keyword arguments:
    id -- The id of the event being deleted.
    """
    # Delete the challenge which matches the given id.
    Event.query.filter(Event.id == id).delete()
    db.session.commit()

    # Return the events page
    return redirect("/events")
