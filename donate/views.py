# IMPORTS
from flask import Blueprint, render_template

# CONFIG
donate_blueprint = Blueprint("donate", __name__, template_folder="templates")


# VIEWS
# view feed homepage
@donate_blueprint.route('/donate')
def donate():
    return render_template('html/index.html')
