import socket
from flask import Flask, render_template

app = Flask(__name__)

# configuration TODO

# logging TODO

# initialise database TODO

# security headers TODO

# home page views
@app.route('/')
def index():
    return render_template('index.html')

# error page views TODO


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

    # register blueprints with app
    app.register_blueprint(users_blueprint)

    app.run(host=my_host, port=free_port, debug=True)


