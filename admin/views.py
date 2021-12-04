# IMPORTS
from flask import Blueprint, render_template
from flask_login import current_user

# CONFIG
admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


# VIEWS
# view admin homepage
@admin_blueprint.route('/admin')
def admin():
    return render_template('admin.html', name=current_user.firstname)