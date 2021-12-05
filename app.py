# IMPORTS
import socket
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import sshtunnel

# Set up SSH tunnel to connect to the database.
tunnel = sshtunnel.SSHTunnelForwarder(
    ("linux.cs.ncl.ac.uk"), ssh_username=os.environ["SSH_USERNAME"], ssh_password=os.environ["SSH_PASSWORD"],
    remote_bind_address=("cs-db.ncl.ac.uk", 3306)
)

tunnel.start()

# CONFIG
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://csc2033_team19:SeerMid._Dim@127.0.0.1:{" \
                                        f"{tunnel.local_bind_port}/csc2033_team19 "
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'


# LOGGING TODO

# initialise database TODO
db = SQLAlchemy(app)

# security headers TODO


# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('index.html')

# ERROR PAGE VIEWS TODO


if __name__ == '__main__':
    my_host = "127.0.0.1"
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((my_host, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()

    # BLUEPRINTS
    # import blueprints
    from users.views import users_blueprint
    from admin.views import admin_blueprint
    from feed.views import feed_blueprint
    from calculator.views import calculator_blueprint
    from donate.views import donate_blueprint

    # register blueprints with app
    app.register_blueprint(users_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(calculator_blueprint)
    app.register_blueprint(feed_blueprint)
    app.register_blueprint(donate_blueprint)

    app.run(host=my_host, port=free_port, debug=True)
