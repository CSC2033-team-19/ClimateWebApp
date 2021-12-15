# Import flask modules
import decimal

from flask_wtf import FlaskForm
from wtforms import SubmitField, DecimalField, DecimalRangeField, SelectField
from wtforms.validators import DataRequired, ValidationError, NumberRange


PLACEHOLDER_VALUES = {
    # VEHICLES
    "public_transport": 94,
    "air_travel": 55,
    "vehicle_fuel": 97,
    "vehicle_upkeep": 108,

    # HOME UTILITIES
    "electricity": 97,
    "gas": 95,
    "heating_oil": 55,
    "water": 33,

    # FOOD
    "meat": 27,
    "fruit_vegetables": 40,
    "dairy": 24,
    "grains": 46,
    "snacks_drinks": 37,

    # OTHER
    "goods": 733,
    "services": 1000
}

# Validators
def validate_positive(form, field):
    print(f"{field.id}: {field.data}")
    if type(field.data) != decimal.Decimal:
        raise ValidationError(f"{field.id} must contain a number.")

    if field.data < 0:
        raise ValidationError(f"{field.id} must contain a positive value.")


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
