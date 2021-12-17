# Import modules
from app import db
from calculator.forms import CalculatorForm
from calculator.forms import PLACEHOLDER_VALUES
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import current_user, login_required
import logging
from models import CarbonData

# Config
calculator_blueprint = Blueprint("calculator", __name__, template_folder="templates")

# Define constants
EMISSION_FACTORS = {
    # Data available at (UKGovt 2018, https://bit.ly/32XfQpo)

    # TODO review data to find better values
    # Travel data
    "aviation": 0.18277,
    "public_transport": 0.09,
    "petrol": 4.39,
    "diesel": 0.918,
    "other": 0.918,
    "vehicle_upkeep": 0.519,

    # Home utilities
    "electricity": 2.249,
    "water": 0.31,
    "gas": 6.966,
    "heating": 0.528,

    # Food
    "meat": 2.471,
    "fruit_vegetables": 0.072,
    "dairy": 0.454,
    "grains": 0.154,
    "snacks_drinks": 0.458,

    # Other expenses
    "goods": 0.59,
    "services": 0.7
}


# Views
@calculator_blueprint.route("/calculator", methods=["GET", "POST"])
@login_required
def calculator():
    form = CalculatorForm()

    if form.validate_on_submit():

        # Calculate the emissions given the user's budget inputs
        travel = get_travel_emissions(
            form.public_transport.data,
            form.air_travel.data,
            form.vehicle_fuel.data,
            form.vehicle_type.data,
            form.vehicle_upkeep.data
        )
        home = get_home_emissions(
            form.electricity.data,
            form.clean_electricity_factor.data,
            form.gas.data,
            form.heating_oil.data,
            form.water.data
        )
        food = get_food_emissions(
            form.meat.data,
            form.grains.data,
            form.dairy.data,
            form.fruit_vegetables.data,
            form.snacks.data
        )
        other_shopping = get_shopping_emissions(
            form.goods.data,
            form.services.data
        )
        # Given the emissions from all the sources, calculate the total emissions
        total_emissions = travel + home + food + other_shopping

        # Get the current user
        user = current_user

        new_carbon_data = CarbonData(user,
                                           total_emissions,
                                           travel,
                                           home,
                                           food,
                                           other_shopping)

        # Add the new data into the database.
        db.session.add(new_carbon_data)
        db.session.commit()

        # Report new data entry using logging.

        logging.warning(f"SECURITY - Carbon data committed to database [{user.id, request.remote_addr}]")

        print("success")

        return render_template("calculator.html",
                               form=form,
                               success=True,
                               toast_body="Successfully saved your carbon footprint data!")

    return render_template("calculator.html", form=form)


@calculator_blueprint.route("/calculator/preview_values.json", methods=["GET"])
def preview_results():
    """
    Show the user a preview of their results.
    """

    handle_input = {}

    # Get rid of the submit button

    for argument in request.args:
        # argument does not need to be tested if it is of vehicle type, and should not be included if it

        if argument != "vehicle_type" and argument != "submit":
            try:
                # If the value is valid, use the given value
                handle_input[argument] = float(request.args.get(argument))
            except ValueError:
                # If the value is invalid, then use the mean value for the emission factor
                handle_input[argument] = PLACEHOLDER_VALUES[argument]

    # Set the values to be returned
    emission_preview = {"travel": get_travel_emissions(
        handle_input["public_transport"],
        handle_input["air_travel"],
        handle_input["vehicle_fuel"],
        request.args.get("vehicle_type"),
        handle_input["vehicle_upkeep"],
    ), "home": get_home_emissions(
        handle_input["electricity"],
        handle_input["clean_electricity_factor"] / 100,
        handle_input["gas"],
        handle_input["heating_oil"],
        handle_input["water"],
    ), "food": get_food_emissions(
        handle_input["meat"],
        handle_input["grains"],
        handle_input["fruit_vegetables"],
        handle_input["dairy"],
        handle_input["snacks"],
    ), "other": get_shopping_emissions(
        handle_input["goods"],
        handle_input["services"]
    )}

    emission_preview["total"] = sum(emission_preview.values())

    return jsonify(emission_preview)


# Functions for calculating emissions
def get_travel_emissions(public_transport, air_travel, vehicle_fuel, vehicle_type, vehicle_upkeep):
    """
    Calculate the total emissions from travel per month
    :param public_transport: The monthly expenditure on public transport
    :param air_travel: The monthly expenditure on air travel
    :param vehicle_fuel: The monthly expenditure on fuel
    :param vehicle_type: Which type of fuel the vehicle uses (Petrol, Diesel, or Other)
    :param vehicle_upkeep: The monthly expenditure on maintenance
    :return: returns the total emissions from travel per month
    """
    return (EMISSION_FACTORS["public_transport"] * float(public_transport)) \
        + (EMISSION_FACTORS["aviation"] * float(air_travel)) \
        + (EMISSION_FACTORS[vehicle_type.lower()] * float(vehicle_fuel)) \
        + (EMISSION_FACTORS["vehicle_upkeep"] * float(vehicle_upkeep))


def get_home_emissions(electricity, clean_electricity_factor, gas, heating, water):
    """
    Calculate the total emissions from household utilities per month
    :param electricity: The monthly expenditure on electricity
    :param clean_electricity_factor: How much electricity comes from a clean source
    :param gas: The monthly expenditure on natural gas
    :param heating: The monthly expenditure on kerosene heating oil
    :param water: The monthly expenditure on water costs
    :return: returns the total emissions from household utilities per month
    """
    return (EMISSION_FACTORS["electricity"] * float(electricity) * (1 - float(clean_electricity_factor / 100))) \
        + (EMISSION_FACTORS["gas"] * float(gas)) \
        + (EMISSION_FACTORS["heating"] * float(heating)) \
        + (EMISSION_FACTORS["water"] * float(water))


def get_food_emissions(meat, grains, fruit_vegetables, dairy, snacks_drinks):
    """
    Calculate the total emissions from food per month
    :param meat: Average monthly expenditure on meat
    :param grains: Average monthly expenditure on grains/baked goods
    :param fruit_vegetables: Average monthly expenditure on fruit/vegetables
    :param dairy: Average monthly expenditure on dairy products
    :param snacks_drinks: Average monthly expenditure on snacks/drinks
    :return: returns the total emissions from food per month
    """
    return (EMISSION_FACTORS["meat"] * float(meat)) \
        + (EMISSION_FACTORS["grains"] * float(grains)) \
        + (EMISSION_FACTORS["fruit_vegetables"] * float(fruit_vegetables)) \
        + (EMISSION_FACTORS["dairy"] * float(dairy)) \
        + (EMISSION_FACTORS["snacks_drinks"] * float(snacks_drinks))


def get_shopping_emissions(goods, services):
    """
    Calculate the total emissions from other expenditures per month
    :param goods: Tangible things that the user has bought, IE, furniture, dvds, etc.
    :param services: Non-tangible things/experiences. IE, medical expenses, vet expenses, consultancy expenses etc.
    :return: returns the total emissions from other expenditures per month
    """
    return (EMISSION_FACTORS["goods"] * float(goods)) \
        + (EMISSION_FACTORS["services"] * float(services))
