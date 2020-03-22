import os

from flask import Flask, render_template, request, session, abort, escape, \
                  url_for, redirect
from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView
from flask_login import LoginManager, login_user, login_required, logout_user,\
                        current_user
from werkzeug.exceptions import default_exceptions, HTTPException
from functions import security

from app.models import db, User, AnonymousUser, Pizza, NonPizza, Topping, \
                       Order, OrderItem, Product
from app.adminviews import AdminView, MenuView, OrderView, ProductView
# , AdminUserIndexView

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
admin = Admin(app, index_view=AdminIndexView())
admin.add_view(AdminView(User, db.session))
admin.add_view(MenuView(Pizza, db.session))
admin.add_view(MenuView(Topping, db.session))
admin.add_view(MenuView(NonPizza, db.session))
admin.add_view(OrderView(Order, db.session))
admin.add_view(OrderView(OrderItem, db.session))
admin.add_view(ProductView(Product, db.session))

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user:
        return user
    else:
        return None


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
            forbidden = ["log", "static", "register", "admin", "user", "pizza",
                         "nonpizza", "extra", "topping", "order", "orderitem",
                         "product", "cart"]
            login_req = ["menu"]

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    register a new user

    aborts if:
        - a user is already registering (403)
        - no username/password/retype password is given (400)
        - user already registered (400)
        - request is anything else than "POST" or "GET" (405)

    returns the register form again if the retype password and password
        weren't the same or the request was a "GET" request. If registration
        was successfull it redirects (303) to "/".
    """

    # get url list from session
    url_list = session.get("urls")

    if request.method not in request.url_rule.methods:
        abort(405)

    # check if request was a "POST" request
    if request.method == "POST":

        # check if user is already registering if so abort 403
        if session.get("register_user") is not None:

            # remove registering user from session
            session.pop("register_user", None)
            abort(403, "Detected double submission of form please try again")

        # get all values from the submitted form
        first_name = escape(request.form.get("register_first_name"))
        last_name = escape(request.form.get("register_last_name"))
        username = escape(request.form.get("register_username"))
        password = escape(request.form.get("register_password"))
        rpassword = escape(request.form.get("register_rpassword"))
        email = escape(request.form.get("register_email"))

        # if the given passwords aren't the same rerender the template
        if password != rpassword:
            return render_template("register.html", message="passwords weren't"
                                   " the same...", urls=url_list)

        # if no username/password/retype password were given abort (400)
        if not username or not password or not rpassword:

            # abort using a 400 HTTPException
            abort(400, "No username/password specified")

        session["register_user"] = username

        user = User.query.filter_by(username=username).all()

        # if username was found in the database abort (400)
        if len(user) >= 1:

            # abort using a 400 HTTPException
            abort(400, "User already registered")

        # add user to database
        register_user = User(first_name=first_name, last_name=last_name,
                             password=password, username=username, email=email)
        db.session.add(register_user)
        db.session.commit()

        # remove registering user from session
        session.pop("register_user", None)

        return redirect("/", 303)

    # check if request was a "GET" request
    elif request.method == "GET":

        return render_template("register.html", urls=url_list)


@app.route("/login", methods=["POST"])
def login():
    if request.method != "POST":
        abort(405)

    username = escape(request.form.get("username"))
    password = escape(request.form.get("password"))

    if not username or not password:

        # abort using a 400 HTTPException
        abort(400, "No username/password specified")

    user_login = User.query.filter_by(username=username).first()

    if not user_login:

        # abort using a 400 HTTPException
        abort(404, "Not found")

    if security.compare_hash(user_login.password, password):
        login_user(user_login)
    else:
        abort(403)

    return redirect(url_for("menu"))


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    if request.method != "GET":
        abort(405)
    logout_user()
    return redirect(url_for("index"), 303)


@app.route("/menu", methods=["GET"])
@login_required
def menu():
    if request.method != "GET":
        abort(405)

    urls = session.get("urls")

    menu = dict()

    pizza_types = [item.pizzatype for item in Pizza.query.
                   with_entities(Pizza.pizzatype).distinct().all()]
    nonpizza_types = [item.type_name for item in NonPizza.query.
                      with_entities(NonPizza.type_name).distinct().all()]

    toppings = Topping.query.all()

    for pizza_type in pizza_types:
        menu[pizza_type] = Pizza.query.filter_by(pizzatype=pizza_type).all()

    for nonpizza_type in nonpizza_types:
        menu[nonpizza_type] = \
            NonPizza.query.filter_by(type_name=nonpizza_type).all()

    return render_template("menu.html", urls=urls, menu=menu, tops=toppings)


@app.route("/cart", methods=["GET", "POST"])
@login_required
def shoppingcart():

    if request.method not in request.url_rule.methods:
        abort(405)

    urls = session.get("urls")

    if request.method == "GET":
        orders = current_user.order

        for order in orders:
            if not order.checkedout:
                details = order.order_details()
        return render_template("cart.html", urls=urls, details=details)

    return render_template("index.html", urls=urls)


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
