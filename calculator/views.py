# Import modules
from calculator.forms import CalculatorForm
from flask import Blueprint, render_template, request, flash
from flask_login import current_user, login_required
from json import dumps

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
# @login_required
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

        # TODO Pass this to the database and re-render the page

    return render_template("calculator.html", form=form)


@calculator_blueprint.route("/calculator/preview_values.json", methods=["GET"])
def preview_results():
    """
    Show the user a preview of their results.
    """

    #TODO error handling

    emission_preview = {"travel": get_travel_emissions(
        float(request.args.get("public_transport")),
        float(request.args.get("air_travel")),
        float(request.args.get("vehicle_fuel")),
        request.args.get("vehicle_type"),
        float(request.args.get("vehicle_upkeep")),
    ), "home": get_home_emissions(
        float(request.args.get("electricity")),
        float(request.args.get("clean_electricity_factor")) / 100,
        float(request.args.get("gas")),
        float(request.args.get("heating_oil")),
        float(request.args.get("water")),
    ), "food": get_food_emissions(
        float(request.args.get("meat")),
        float(request.args.get("grains")),
        float(request.args.get("fruit_vegetables")),
        float(request.args.get("dairy")),
        float(request.args.get("snacks")),
    ), "other": get_shopping_emissions(
        float(request.args.get("goods")),
        float(request.args.get("services"))
    )}

    return dumps(emission_preview)


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
    return (EMISSION_FACTORS["public_transport"] * public_transport) \
        + (EMISSION_FACTORS["aviation"] * air_travel) \
        + (EMISSION_FACTORS[vehicle_type.lower()] * vehicle_fuel) \
        + (EMISSION_FACTORS["vehicle_upkeep"] * vehicle_upkeep)


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
    return (EMISSION_FACTORS["electricity"] * electricity * (1 - clean_electricity_factor)) \
        + (EMISSION_FACTORS["gas"] * gas) \
        + (EMISSION_FACTORS["heating"] * heating) \
        + (EMISSION_FACTORS["water"] * water)


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
    return (EMISSION_FACTORS["meat"] * meat) \
        + (EMISSION_FACTORS["grains"] * grains) \
        + (EMISSION_FACTORS["fruit_vegetables"] * fruit_vegetables) \
        + (EMISSION_FACTORS["dairy"] * dairy) \
        + (EMISSION_FACTORS["snacks_drinks"] * snacks_drinks)


def get_shopping_emissions(goods, services):
    """
    Calculate the total emissions from other expenditures per month
    :param goods: Tangible things that the user has bought, IE, furniture, dvds, etc.
    :param services: Non-tangible things/experiences. IE, medical expenses, vet expenses, consultancy expenses etc.
    :return: returns the total emissions from other expenditures per month
    """
    return (EMISSION_FACTORS["goods"] * goods) \
        + (EMISSION_FACTORS["services"] * services)
