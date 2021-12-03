from flask import Flask

app = Flask(__name__)

# configuration TODO

# logging TODO

# initialise database TODO

# security headers TODO

# home page views
@app.route('/')
def hello_world():
    return 'Welcome to Greenify!!'

# error page views TODO


if __name__ == '__main__':
    app.run()


