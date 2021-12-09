# IMPORTS
import logging
import socket
from functools import wraps

from flask import Flask, render_template, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
import os
import sshtunnel

# Set up SSH tunnel to connect to the database.
# tunnel = sshtunnel.SSHTunnelForwarder(
# ("linux.cs.ncl.ac.uk"), ssh_username=os.environ["SSH_USERNAME"], ssh_password=os.environ["SSH_PASSWORD"],
# remote_bind_address=("cs-db.ncl.ac.uk", 3306)
# )

# tunnel.start()

# CONFIG
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://csc2033_team19:SeerMid._Dim@127.0.0.1:{" \
# f"{tunnel.local_bind_port}/csc2033_team19 "
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'

# DB FOR TESTING
#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+pymysql://csc2033_team19:SeerMid._Dim@cs-db.ncl.ac.uk:3306/csc2033_team19'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'

# DB FOR TESTING
app = Flask(__name__)
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///greenify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# FUNCTIONS
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logging.warning('SECURITY - Unauthorised access attempt [%s, %s, %s, %s]',
                                current_user.id,
                                current_user.username,
                                current_user.role,
                                request.remote_addr)
                # Redirect the user to an unauthorised notice!
                return render_template('403.html')
            return f(*args, **kwargs)

        return wrapped

    return wrapper


# LOGGING TODO

# initialise database TODO
db = SQLAlchemy(app)


# security headers TODO


# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('index.html')


# ERROR PAGE VIEWS
@app.errorhandler(400)
def page_forbidden(error):
    return render_template('400.html'), 400


@app.errorhandler(403)
def page_forbidden(error):
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.errorhandler(503)
def page_forbidden(error):
    return render_template('503.html'), 503


if __name__ == '__main__':
    my_host = "127.0.0.1"
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((my_host, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()

    # LOGIN MANAGER

    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models import User


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    # BLUEPRINTS
    # import blueprints
    from users.views import users_blueprint
    from admin.views import admin_blueprint
    from challenges.views import challenges_blueprint
    from posts.views import posts_blueprint
    from calculator.views import calculator_blueprint
    from donate.views import donate_blueprint

    # register blueprints with app
    app.register_blueprint(users_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(challenges_blueprint)
    app.register_blueprint(posts_blueprint)
    app.register_blueprint(calculator_blueprint)
    app.register_blueprint(donate_blueprint)

    app.run(host=my_host, port=free_port, debug=True)
