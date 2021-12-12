# Import flask modules
from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField, DecimalRangeField, SelectField
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
    if type(field.data) != float or type(field.data) != int:
        raise ValidationError(f"{field.id} must contain a number.")

    if field.data < 0:
        raise ValidationError(f"{field.id} must contain a positive value.")


class CalculatorForm(FlaskForm):
    """
    Creates a form for the user to enter their carbon emission data

    All placeholder data is from ONS TODO verify data
    """

    # Transportation
    public_transport = FloatField(validators=[DataRequired(), validate_positive],
                                  render_kw={"placeholder": PLACEHOLDER_VALUES["public_transport"]})
    air_travel = FloatField(validators=[DataRequired(), validate_positive],
                            render_kw={"placeholder": PLACEHOLDER_VALUES["air_travel"]})
    vehicle_fuel = FloatField(validators=[DataRequired(), validate_positive],
                              render_kw={"placeholder": PLACEHOLDER_VALUES["vehicle_fuel"]})
    vehicle_type = SelectField(validators=[DataRequired(), validate_positive],
                               label="Fuel", choices=["Diesel", "Petrol", "Other"])
    vehicle_upkeep = FloatField(validators=[DataRequired(), validate_positive],
                                render_kw={"placeholder": PLACEHOLDER_VALUES["vehicle_upkeep"]})

    # Home utilities
    electricity = FloatField(validators=[DataRequired(), validate_positive],
                             render_kw={"placeholder": PLACEHOLDER_VALUES["electricity"]})
    clean_electricity_factor = DecimalRangeField(default=0, validators=[DataRequired(), NumberRange(1, 100)],
                                                 render_kw={"step": 1,
                                                            "data-bs-toggle": "tooltip",
                                                            "data-bs-placement": "top",
                                                            "data-bs-animation": False
                                                            })
    gas = FloatField(validators=[DataRequired(), validate_positive],
                     render_kw={"placeholder": PLACEHOLDER_VALUES["gas"]})
    heating_oil = FloatField(validators=[DataRequired(), validate_positive],
                             render_kw={"placeholder": PLACEHOLDER_VALUES["heating_oil"]})
    water = FloatField(validators=[DataRequired(), validate_positive],
                       render_kw={"placeholder": PLACEHOLDER_VALUES["water"]})

    # Food shopping
    meat = FloatField(validators=[DataRequired(), validate_positive],
                      render_kw={"placeholder": PLACEHOLDER_VALUES["meat"]})
    fruit_vegetables = FloatField(validators=[DataRequired(), validate_positive],
                                    render_kw={"placeholder": PLACEHOLDER_VALUES["fruit_vegetables"]})
    dairy = FloatField(validators=[DataRequired(), validate_positive],
                       render_kw={"placeholder": PLACEHOLDER_VALUES["dairy"]})
    grains = FloatField(validators=[DataRequired(), validate_positive],
                        render_kw={"placeholder": PLACEHOLDER_VALUES["grains"]})
    snacks = FloatField(validators=[DataRequired(), validate_positive],
                        render_kw={"placeholder": PLACEHOLDER_VALUES["snacks_drinks"]})

    # Other expenditures
    goods = FloatField(validators=[DataRequired(), validate_positive],
                       render_kw={"placeholder": PLACEHOLDER_VALUES["goods"]})
    services = FloatField(validators=[DataRequired(), validate_positive],
                          render_kw={"placeholder": PLACEHOLDER_VALUES["services"]})

    # Submit field
    submit = SubmitField()
