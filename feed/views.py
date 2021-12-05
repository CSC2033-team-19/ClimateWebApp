# IMPORTS
from flask import Blueprint, render_template
from flask_login import current_user

# CONFIG
feed_blueprint = Blueprint('feed', __name__, template_folder='templates')


# VIEWS
# view feed homepage
@feed_blueprint.route('/feed')
def feed():
    return render_template('feed.html', name=current_user.firstname)