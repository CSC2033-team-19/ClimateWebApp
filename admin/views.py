from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import requires_roles
from models import User

# CONFIG
admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


# ROUTES
# view admin homepage
@admin_blueprint.route('/admin')
@login_required
@requires_roles('admin')
def admin():
    return render_template('admin.html',
                           name=current_user.firstname,)


# view all registered users
@admin_blueprint.route('/view_all_users', methods=['POST'])
@login_required
@requires_roles('admin')
def view_all_users():
    return render_template('admin.html', name=current_user.firstname, current_users=User.query.all())


# view last 10 log entries
@admin_blueprint.route('/logs', methods=['POST'])
@login_required
@requires_roles('admin')
def logs():
    with open("climatewebapp.log", "r") as f:
        content = f.read().splitlines()[-10:]
        content.reverse()

    return render_template('admin.html', logs=content, name=current_user.firstname)
