"""
This module will create a form, and handle input validation for the creation/updating of events for the map
"""

__author__ = "Adam Winstanley"

# Import flask modules
import os

import wtforms
from flask_wtf import FlaskForm
from wtforms import SubmitField, DecimalField, DecimalRangeField, SelectField, StringField, IntegerField, TimeField
from wtforms.validators import DataRequired, ValidationError, NumberRange
import requests
from datetime import datetime, timedelta


GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


class EventForm(FlaskForm):
    """
    Creates a form for the user to enter a new event
    """

    def check_date_format(self, field):
        """
        Validate that the date entered into the form is in the correct format.
        """
        try:
            datetime.strptime(self.date.data, "%d-%m-%Y")
        except ValueError:
            raise ValidationError("Date is not in the correct format (DD-MM-YYYY)")

    def in_future(self, field):
        """
        Check if the event entered is in the future
        """
        if datetime.now() + timedelta(7) > self.get_date_time():
            raise ValidationError("Please give your guests ample time to attend the event.")

    def get_date_time(self):
        """
        Combine the date and time fields.
        """
        date = datetime.strptime(self.date.data, "%d-%m-%Y")
        date = date.replace(hour=self.time.data.hour, minute=self.time.data.minute)

        return date

    def get_lat_lng(self, field):
        """
        Get the latitude and longitude of the event using geocoding.
        """
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

    def fill_data(self, event):
        """
        Prefill out the form with given data.
        """
        self.head.data = event.head
        self.body.data = event.body
        self.capacity.data = event.capacity
        self.date.data = f"{str(event.time.day).zfill(2)}-{str(event.time.month).zfill(2)}-{event.time.year}"
        self.time.data = event.time
        self.address.data = event.address
