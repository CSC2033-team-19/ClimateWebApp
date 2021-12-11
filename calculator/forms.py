# Import flask modules
from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField, DecimalRangeField, SelectField
from wtforms.validators import DataRequired, ValidationError, NumberRange


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
    public_transport = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 94})
    air_travel = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 55})
    vehicle_fuel = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 1164})
    vehicle_type = SelectField(validators=[DataRequired(), validate_positive], label="Fuel", choices=["Diesel", "Petrol", "Other"])
    vehicle_upkeep = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 108})

    # Home utilities
    electricity = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 97})
    clean_electricity_factor = DecimalRangeField(default=0, validators=[DataRequired(), NumberRange(1, 100)],
                                                 render_kw={"step": 1,
                                                            "data-bs-toggle": "tooltip",
                                                            "data-bs-placement": "top",
                                                            "data-bs-animation": False
                                                            })
    gas = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 95})
    heating_oil = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 55})
    water = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 33})

    # Food shopping
    meat = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 27})
    fruit_vegetables = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 40})
    dairy = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 24})
    grains = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 46})
    snacks = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 37})

    # Other expenditures
    goods = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 733})
    services = FloatField(validators=[DataRequired(), validate_positive], render_kw={"placeholder": 1000})

    # Submit field
    submit = SubmitField()
