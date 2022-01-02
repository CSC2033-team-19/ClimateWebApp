# Import flask modules
import os

import wtforms
from flask_wtf import FlaskForm
from wtforms import SubmitField, DecimalField, DecimalRangeField, SelectField, StringField, IntegerField, TimeField
from wtforms.validators import DataRequired, ValidationError, NumberRange
import requests
from datetime import datetime


GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


class EventForm(FlaskForm):
    """
    Creates a form for the user to enter a new event
    """

    # Validate the date is in the correct format
    def check_date_format(self, field):
        try:
            datetime.strptime(self.date.data, "%d-%m-%Y")
        except ValueError:
            raise ValidationError("Date is not in the correct format (DD-MM-YYYY)")

    # Validate the date is not in the past
    def in_future(self, field):
        if datetime.now() > self.get_date_time():
            raise ValidationError("You cannot hold an event in the past")

    # Get the datetime object to put in the database.
    def get_date_time(self):
        date = datetime.strptime(self.date.data, "%d-%m-%Y")

        date = date.replace(hour=self.time.data.hour, minute=self.time.data.minute)

        return date

    def get_lat_lng(self, field):
        # Request from google's geocoding service, bias towards uk
        req = requests.get(GEOCODE_URL, {"address": self.address, "key": os.environ["GMAP-KEY"], "region": "uk"})

        # If the address was found, store the results
        if req.json()["status"] == "OK":
            # Ensure address is consistent with latlng
            self.address.data = req.json()["results"][0]["formatted_address"]

            # Get latlng from request to geocoding service
            self.lat = req.json()["results"][0]["geometry"]["location"]["lat"]
            self.lng = req.json()["results"][0]["geometry"]["location"]["lng"]
        else:
            # The address was not found. display error
            raise ValidationError("That address could not be found")

    # Create forms with required validation
    head = StringField(validators=[DataRequired()])
    body = StringField(validators=[DataRequired()])
    capacity = IntegerField(validators=[DataRequired(), NumberRange(min=1, max=None, message="Minimum attendees is 1")])
    date = StringField(validators=[DataRequired(), check_date_format, in_future])
    time = TimeField(validators=[DataRequired()])
    address = StringField(validators=[DataRequired(), get_lat_lng])
    submit = SubmitField()

    # Fill out data in form for updating the event
    def fill_data(self, event):
        self.head.data = event.head
        self.body.data = event.body
        self.capacity.data = event.capacity
        self.date.data = f"{str(event.time.day).zfill(2)}-{str(event.time.month).zfill(2)}-{event.time.year}"
        self.time.data = event.time
        self.address.data = event.address
