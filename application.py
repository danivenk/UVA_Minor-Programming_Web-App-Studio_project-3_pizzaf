#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
version: python 3+
application.py defines flask application
Dani van Enk, 11823526
"""

# used imports
import os
from datetime import date

from flask import Flask, render_template, request, session, abort, escape, \
                  url_for, redirect
from flask_session import Session
from flask_migrate import Migrate
from flask_admin import Admin
from flask_login import LoginManager, login_user, login_required, logout_user,\
                        current_user
from werkzeug.exceptions import default_exceptions, HTTPException
from functions import security

from app.models import db, User, AnonymousUser, Pizza, NonPizza, Topping, \
                       Order, OrderItem, Product
from app.adminviews import AdminView, MenuView, OrderView, ProductView, \
                        AdminUserIndexView

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
admin = Admin(app, index_view=AdminUserIndexView())
admin.add_view(AdminView(User, db.session))
admin.add_view(MenuView(Pizza, db.session))
admin.add_view(MenuView(Topping, db.session))
admin.add_view(MenuView(NonPizza, db.session))
admin.add_view(ProductView(Product, db.session))
admin.add_view(OrderView(OrderItem, db.session))
admin.add_view(OrderView(Order, db.session))

# login setup
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """
    load a user into the login manager
    """

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
            login_req = ["menu", "recent"]

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
    url_list = dict(sorted(url_list.items()))

    # add url_list to session
    session["urls"] = url_list


@app.route("/", methods=["GET"])
def index():
    """
    show the index page of the site

    abort if:
        - request is anthing else than "GET" (405)
    """

    # get url list from session
    url_list = session.get("urls")

    # abort using a 405 if request method is not "GET"
    if request.method not in request.url_rule.methods:
        abort(405)

    return render_template("index.html", urls=url_list)


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

    # abort using a 405 if request method is not "POST" or "GET"
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

        # add registering user to session
        session["register_user"] = username

        # look for username in database
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
    """
    log user in if the right crendentials are given

    abort if:
        - request is anything else than "POST" (405);
        - if no crendentials are given (400);
        - if user not in database (404);
        - if wrong credentials are given (403);

    returns a redirect to menu if logged on (303)
    """

    # abort using a 405 if request method is not "POST"
    if request.method != "POST":
        abort(405)

    # get the username and password from the login form
    username = escape(request.form.get("username"))
    password = escape(request.form.get("password"))

    # if no credentials are given abort using 400 HTTPException
    if not username or not password:

        abort(400, "No username/password specified")

    # look for user in database
    user_login = User.query.filter_by(username=username).first()

    # is user not found in database abort using 404 HTTPException
    if not user_login:

        abort(404, "Not found")

    # check if credentials are correct
    #   login if correct, abort using 403 HTTPException if not
    if security.compare_hash(user_login.password, password):
        login_user(user_login)
    else:
        abort(403)

    return redirect(url_for("menu"), 303)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """
    log logged on user out, LOGIN REQUIRED

    abort if:
        - request anything else than "GET";

    return redirect to index (303)
    """

    # abort using a 405 if request method is not "GET"
    if request.method != "GET":
        abort(405)

    # logout user
    logout_user()

    return redirect(url_for("index"), 303)


@app.route("/menu", methods=["GET"])
@login_required
def menu():
    """
    shows the menu, LOGIN REQUIRED

    aborts if:
        - request is anything else than a "GET" request (405);

    returns the menu
    """

    # abort using a 405 if request method is not "GET"
    if request.method != "GET":
        abort(405)

    # get url list from session
    url_list = session.get("urls")

    # create an empty dictionary for the menu and an empty list for the links
    menu = dict()
    menu_links = []

    # get all pizza and nonpizza types
    pizza_types = [item.pizzatype for item in Pizza.query.
                   with_entities(Pizza.pizzatype).distinct().all()]
    nonpizza_types = [item.type_name for item in NonPizza.query.
                      with_entities(NonPizza.type_name).distinct().all()]

    # get all toppings
    toppings = Topping.query.all()

    # add all pizzas to the menu and to the menu link list
    for pizza_type in pizza_types:
        menu[pizza_type] = Pizza.query.filter_by(pizzatype=pizza_type).all()
        menu_links.append(pizza_type.lower())

    # add all non-pizzas to the menu and to the menu link list
    for nonpizza_type in nonpizza_types:
        menu[nonpizza_type] = \
            NonPizza.query.filter_by(type_name=nonpizza_type).all()
        menu_links.append(nonpizza_type.lower())

    return render_template("menu.html", urls=url_list, menu=menu,
                           tops=toppings, menu_links=menu_links)


def add_pizza(item_id, request):
    """
    adds pizza to products if not available already and returns this product

    parameters:
        item_id - id of the pizzza;
        request - the post request to get the pizza product;

    returns the product
    """

    # get the pizza for which the id is given
    pizza = Pizza.query.get(item_id)

    # create an empty topping list
    toppings = []

    # get all toppings the user wants
    for topping_id in range(pizza.no_toppings):
        topping_name = request.form.get(f"topping{topping_id}")
        toppings.append(
            Topping.query.filter_by(
                topping_name=topping_name).first())

    # sort the toppings by topping name
    toppings = sorted(toppings, key=lambda x: x.topping_name)

    # look for the pizza in the database
    products = Product.query.join(Pizza).filter_by(id=item_id).all()

    # if none found define an empty current_product
    if len(products) == 0:
        current_product = None

    # loop over the products in the database with the correct pizza id
    #   and check against requested toppings
    for product in products:
        if sorted(product.toppings, key=lambda x: x.topping_name) \
                == toppings:
            current_product = product
        else:
            current_product = None

    # if nothing has been found in the database create a new product
    if not current_product:
        current_product = Product(pizza=pizza, toppings=toppings)

        db.session.add(current_product)
        db.session.commit()

    return current_product


def add_nonpizza(item_id, request):
    """
    add nonpizza to products if not available already and returns this product

    parameters:
        item_id - id of the non-pizza;
        request - the post request to get the non-pizza product;

    returns the product
    """

    # get the non-pizza for wich the id is given
    nonpizza = NonPizza.query.get(item_id)

    # get cheese choice from from
    extra_cheese = request.form.get("cheese")

    if extra_cheese:
        extra = True
    else:
        extra = False

    # look if requested non-pizza is already in database
    products = Product.query.join(NonPizza).filter_by(id=item_id).all()

    # if none found define an empty current_product
    if len(products) == 0:
        current_product = None

    # loop over the products in the database with the correct nonpizza id
    #   and check against requested extra cheese choice
    for product in products:
        if product.extra_cheese:
            current_product = product
        else:
            current_product = None

    # if nothing has been found in the database create a new product
    if not current_product:
        current_product = Product(nonpizza=nonpizza,
                                  extra_cheese=extra)

        db.session.add(current_product)
        db.session.commit()

    return current_product


@app.route("/cart", methods=["GET", "POST"])
@login_required
def shoppingcart():
    """
    show the cart and adds items to the cart, LOGIN REQUIRED

    aborts if:
        - request is not a "GET" or "POST" request (405);

    when using a "POST" request it redirects to itself ("GET")
    """

    # abort using a 405 if request method is not "POST" or "GET"
    if request.method not in request.url_rule.methods:
        abort(405)

    # get url list from session
    url_list = session.get("urls")

    # get the orders of the current user
    orders = current_user.order

    # preset details to None
    details = None

    # check for all orders if there is one not checked out
    for order in orders:

        # save order and details if checkout is false
        if not order.checkedout:
            current_order = order
            details = order.order_details()

    # return the cart if the request is a "GET" request
    if request.method == "GET":
        if details:
            return render_template("cart.html", urls=url_list, details=details)
        else:
            return render_template("cart.html", urls=url_list)

    # if the request is a "POST" request add the item to the cart
    elif request.method == "POST":

        # get the values from the form
        item_type = request.form.get("item_type")
        item_id = request.form.get("item_id")
        quantity = request.form.get("quantity")

        # if there is no active order create a new one
        if not details:
            current_order = Order(user=current_user,
                                  created_date=date.today())
            db.session.add(current_order)
            db.session.commit()

        # get the product to be added by item_type
        if item_type == "Pizza":
            current_product = add_pizza(item_id, request)
        else:
            current_product = add_nonpizza(item_id, request)

        # create a new order-item
        order_item = OrderItem(quantity=quantity,
                               created_date=date.today(),
                               order=current_order,
                               product=current_product)

        # add order-item to current order
        current_order.orderitem.append(order_item)

        db.session.add(order_item)
        db.session.commit()

        return redirect(url_for("shoppingcart"), 303)


@app.route("/checkout", methods=["POST"])
@login_required
def pay_now():
    """
    checks out the current active cart of the user, LOGIN REQUIRED

    aborts if:
        - request is anything else than a "POST" request (405);
        - if the checking out user is not the order user (403);

    if completed redirects to the homepage of the site
    """

    # abort using a 405 if request method is not "POST"
    if request.method != "POST":
        abort(405)

    # get order id from form
    order_id = request.form.get("order")

    # get order from database
    checkout_order = Order.query.get(order_id)

    # check if logged on user is the correct user and check out
    if current_user.get_id() == checkout_order.user.get_id():
        checkout_order.checkedout = True
        db.session.commit()

        """
        POSSIBLE EXTENSION
        ADD HERE PAYMENT METHOD AND/OR MAIL TO USER
        """

        return redirect(url_for("index"))

    return abort(403)


@app.route("/history", methods=["GET"])
@login_required
def recent():
    """
    show the order history of the logged on user, LOGIN REQUIRED

    aborts if:
        - request is anything else than a "GET" request;

    returns the history page
    """

    # abort using a 405 if request method is not "GET"
    if request.method != "GET":
        abort(405)

    # get url list from session
    url_list = session.get("urls")

    # get all orders of the current user sorted in reverse order of id
    orders = sorted(current_user.order, key=lambda x: x.id, reverse=True)

    return render_template("history.html", urls=url_list, orders=orders)


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
