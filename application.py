import os

from flask import Flask, render_template, request, session, abort, escape
from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user
from werkzeug.exceptions import default_exceptions, HTTPException
from functions import security

from app.models import db, User

# Configure Flask app
app = Flask(__name__)

# Configure database
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.secret_key = os.environ['SECRET_KEY']

# Configure session, use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure migrations
Migrate(app, db)

# admin setup
admin = Admin(app, name='Pinocchio Admin', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))

login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.before_request
def setup_urls():
    """
    create a dictionary for the navbar items
    """

    # get all routes in the app
    urls = app.url_map.iter_rules()

    # create an empty dictionary
    url_list = dict()

    # iterate over all routes in the app
    for url in urls:

        # filter for routes with a "GET" method
        if "GET" in url.get_empty_kwargs()["methods"]:

            # get the endpoint of the route
            endpoint = url.get_empty_kwargs()["endpoint"]

            # define the routes excluded and only available if logged on
            forbidden = ["log", "static", "register", "api", "book", "user",
                         "admin"]
            login_req = ["search"]

            # check if allowed
            allowed = not any(item in endpoint for item in forbidden)

            # add index as "Home"
            if "index" in endpoint and allowed:
                url_list[endpoint] = ["Home", None]

            # add items where login is required
            elif any(item in endpoint for item in login_req) and allowed:
                url_list[endpoint] = [endpoint.capitalize(), True]

            # add items the rest
            elif allowed:
                url_list[endpoint] = [endpoint.capitalize(), None]

    # sort dictionary by key
    url_list = dict(sorted(url_list.items(), key=lambda x: x[0]))

    # add url_list to session
    session["urls"] = url_list


@app.route("/")
def index():
    urls = session.get("urls")
    return render_template("index.html", urls=urls)


@app.route("/login", methods=["POST"])
def login():
    if request.method != "POST":
        abort(405)

    username = escape(request.form.get("username"))
    password = escape(request.form.get("password"))

    if not username or not password:

        # abort using a 400 HTTPException
        abort(400, "No username/password specified")

    login_db = User.query.filter_by(username=username).all()

    if len(login_db) != 1:
        abort(400, "found multiple entries of the same username")
    else:
        login = login_db[0]

    if security.compare_hash(login.password, password):
        login_user(login.id)


@app.errorhandler(HTTPException)
def errorhandler(error):
    """
    Handle errors

    used same code as in the exercise similarities

    return error template

    reused part of the code from the Survey and Similarities web apps
        from UVA Mprog Programming 2 Module 10 - Web
    """

    # get url list from session
    url_list = session.get("urls")

    # split the error into the header and message (index, 0 header, 1 text)
    error_message = str(error).split(":")

    # check if someone is logged on
    if "username" in session:

        # get username if so and render
        user = session.get("username")

        return render_template("error.html", header=error_message[0],
                               message=error_message[1], login=True, user=user,
                               urls=url_list), error.code
    else:

        return render_template("error.html", header=error_message[0],
                               message=error_message[1], urls=url_list), \
                error.code


# https://github.com/pallets/flask/pull/2314
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
