"""
This module will render a form for the user to enter their carbon data into.
This handles input validation.
"""

__author__ = "Adam Winstanley"

# Import flask modules
import decimal

from flask_wtf import FlaskForm
from wtforms import SubmitField, DecimalField, DecimalRangeField, SelectField
from wtforms.validators import DataRequired, ValidationError, NumberRange

PRETTY_NAMES = {
    # VEHICLES
    "public_transport": "Public transport",
    "air_travel": "Air travel",
    "vehicle_fuel": "Vehicle fuel",
    "vehicle_upkeep": "Vehicle upkeep",

    # HOME UTILITIES
    "electricity": "Electricity",
    "gas": "Natural gas",
    "heating_oil": "Heating oil",
    "water": "Water",

    # FOOD
    "meat": "Meat",
    "fruit_vegetables": "Fruit & vegetables",
    "dairy": "Dairy products",
    "grains": "Grains & baked products",
    "snacks": "Snacks and drinks",

    # OTHER
    "goods": "Goods",
    "services": "Services"
}

PLACEHOLDER_VALUES = {
    # VEHICLES
    "public_transport": 112,  #(src: https://www.statista.com/statistics/285660/transport-services-weekly-household-expenditure-in-the-united-kingdom-uk-by-age/)
    "air_travel": 55,  #(src: https://www.statista.com/statistics/580052/average-spend-per-trip-abroad-from-the-united-kingdom-uk-by-purpose/)
    "vehicle_fuel": 105,  #(src: https://www.nimblefins.co.uk/largest-car-insurance-companies/average-cost-petrol-car)
    "vehicle_upkeep": 108,  #(src: https://www.moneyshake.com/car-finance-guides/maintaining-your-lease-car/how-much-should-car-maintenance-cost-per-year)

    # HOME UTILITIES
    "electricity": 97,  #(src: https://www.loveenergysavings.com/content-hub/energy-talk/how-much-is-the-average-uk-household-energy-bill/)
    "gas": 39,  #(src: https://www.britishgas.co.uk/energy/guides/average-bill.html)
    "heating_oil": 69,  #(src: https://www.which.co.uk/reviews/home-heating-systems/article/home-heating-systems/oil-central-heating-aP9gU4u5O8aO)
    "water": 33,  #(src: https://www.moneyadviceservice.org.uk/blog/how-much-is-the-average-water-bill-per-month)

    # FOOD
    "meat": 145,  #(src: https://www.nimblefins.co.uk/average-uk-household-cost-food)
    "fruit_vegetables": 48,  #(src: https://www.nimblefins.co.uk/average-uk-household-cost-food)
    "dairy": 101,  #(src: https://www.nimblefins.co.uk/average-uk-household-cost-food)
    "grains": 46,  #(src: https://www.nimblefins.co.uk/average-uk-household-cost-food)
    "snacks_drinks": 70,  #(src: https://www.nimblefins.co.uk/average-uk-household-cost-food)

    # OTHER (general guideline for data, does not give split of goods/services so that is estimated)
    "goods": 780,  #(src: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/bulletins/familyspendingintheuk/april2018tomarch2019)
    "services": 565  #(src: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/bulletins/familyspendingintheuk/april2018tomarch2019)
}


# Validators
def validate_positive(form, field):
    print(f"{field.id}: {field.data}")
    if type(field.data) != decimal.Decimal:
        raise ValidationError(f"{PRETTY_NAMES[field.id]} must contain a number.")

    if field.data < 0:
        raise ValidationError(f"{PRETTY_NAMES[field.id]} must contain a positive value.")


class CalculatorForm(FlaskForm):
    """
    Creates a form for the user to enter their carbon emission data

    All placeholder data is from ONS TODO verify data
    """

    # Transportation
    public_transport = DecimalField(validators=[DataRequired(), validate_positive],
                                    render_kw={"placeholder": PLACEHOLDER_VALUES["public_transport"]})
    air_travel = DecimalField(validators=[DataRequired(), validate_positive],
                              render_kw={"placeholder": PLACEHOLDER_VALUES["air_travel"]})
    vehicle_fuel = DecimalField(validators=[DataRequired(), validate_positive],
                                render_kw={"placeholder": PLACEHOLDER_VALUES["vehicle_fuel"]})
    vehicle_type = SelectField(validators=[DataRequired()],
                               label="Fuel", choices=["Diesel", "Petrol", "Other"])
    vehicle_upkeep = DecimalField(validators=[DataRequired(), validate_positive],
                                  render_kw={"placeholder": PLACEHOLDER_VALUES["vehicle_upkeep"]})

    # Home utilities
    electricity = DecimalField(validators=[DataRequired(), validate_positive],
                               render_kw={"placeholder": PLACEHOLDER_VALUES["electricity"]})
    clean_electricity_factor = DecimalRangeField(default=0, validators=[DataRequired(), NumberRange(1, 100)],
                                                 render_kw={"step": 1,
                                                            "data-bs-toggle": "tooltip",
                                                            "data-bs-placement": "top",
                                                            "data-bs-animation": False
                                                            })
    gas = DecimalField(validators=[DataRequired(), validate_positive],
                       render_kw={"placeholder": PLACEHOLDER_VALUES["gas"]})
    heating_oil = DecimalField(validators=[DataRequired(), validate_positive],
                               render_kw={"placeholder": PLACEHOLDER_VALUES["heating_oil"]})
    water = DecimalField(validators=[DataRequired(), validate_positive],
                         render_kw={"placeholder": PLACEHOLDER_VALUES["water"]})

    # Food shopping
    meat = DecimalField(validators=[DataRequired(), validate_positive],
                        render_kw={"placeholder": PLACEHOLDER_VALUES["meat"]})
    fruit_vegetables = DecimalField(validators=[DataRequired(), validate_positive],
                                    render_kw={"placeholder": PLACEHOLDER_VALUES["fruit_vegetables"]})
    dairy = DecimalField(validators=[DataRequired(), validate_positive],
                         render_kw={"placeholder": PLACEHOLDER_VALUES["dairy"]})
    grains = DecimalField(validators=[DataRequired(), validate_positive],
                          render_kw={"placeholder": PLACEHOLDER_VALUES["grains"]})
    snacks = DecimalField(validators=[DataRequired(), validate_positive],
                          render_kw={"placeholder": PLACEHOLDER_VALUES["snacks_drinks"]})

    # Other expenditures
    goods = DecimalField(validators=[DataRequired(), validate_positive],
                         render_kw={"placeholder": PLACEHOLDER_VALUES["goods"]})
    services = DecimalField(validators=[DataRequired(), validate_positive],
                            render_kw={"placeholder": PLACEHOLDER_VALUES["services"]})

    # Submit field
    submit = SubmitField()
