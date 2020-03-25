#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
version: python 3+
models.py defines all used models and has 1 event_listener for the password
Dani van Enk, 11823526

references:
    https://flask-login.readthedocs.io/en/latest/
    https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
    https://cs50.harvard.edu/web/notes/4/
"""

# used imports
from flask_sqlalchemy import SQLAlchemy, event
from flask_login import AnonymousUserMixin
from functions import security as s

# define SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    """
    The User Class defines a user and is based of db.Model

    tablename: users

    columns:
        id          - user id;
        first_name  - first name of the user;
        last_name   - last name of the user;
        password    - password of the user;
        username    - username of the user;
        admin       - has user admin privileges;
        orders      - orders of the user;

    methods:
        get_id          - gets the id of the user;
        items_in_cart   - checks the number of items in the user's cart;

    properies:
        is_authenticated
        is_active
        is_anonymous
    """

    # database tablename and column setup
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    order = db.relationship("Order")

    def get_id(self):
        """
        returns the id of the user
        """

        return self.id

    def items_in_cart(self):
        """
        returns the number of items in the cart

        if no cart returns none
        """

        for order in self.order:
            if not order.checkedout:
                return f"({order.item_number()})"
        return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __repr__(self):
        """
        returns the representation of the User class
        """

        return self.first_name + " " + self.last_name


class AnonymousUser(AnonymousUserMixin):
    """
    The AnonymousUser Class defines a anonymous user and
    is a based of AnonymousUserMixin

    properies:
        admin - no admin privileges for anonymous users;
    """

    @property
    def admin(self):
        return False


# database tablename and column setup for the association table
#   many-to-many (topping-product)
toppings = db.Table('toppings_association',
                    db.Column('topping_id', db.ForeignKey('toppings.id'),
                              primary_key=True),
                    db.Column('product_id', db.ForeignKey('products.id'),
                              primary_key=True)
                    )


class Pizza(db.Model):
    """
    The Pizza Class defines a pizza and is a based of db.Model

    tablename: pizzas

    columns:
        id          - pizza id;
        pizzatype   - pizza type;
        size        - size of the pizza;
        no_toppings - number of toppings;
        cost        - cost of the pizza;
        product     - products associated with this pizza;
    """

    # database tablename and column setup
    __tablename__ = 'pizzas'
    id = db.Column(db.Integer, primary_key=True)
    pizzatype = db.Column(db.String(128), nullable=False)
    size = db.Column(db.String(128), nullable=False)
    no_toppings = db.Column(db.Integer, nullable=True)
    cost = db.Column(db.Float, nullable=True)
    product = db.relationship("Product")

    def __repr__(self):
        """
        returns the representation of the Pizza class
        """

        # if no toppings show as cheese only
        if self.no_toppings == 0:
            return f"{self.pizzatype} ({self.size}): cheese topping only"
        # show number of allowed toppings
        elif self.no_toppings == 1:
            return f"{self.pizzatype} ({self.size}): {self.no_toppings} " \
                    "topping"
        # is 5 toppings show as special
        elif self.no_toppings == 5:
            return f"{self.pizzatype} ({self.size}): special (5 toppings)"
        return f"{self.pizzatype} ({self.size}): {self.no_toppings} toppings"


class Topping(db.Model):
    """
    The Topping Class defines a topping and is based of db.Model

    tablename: toppings

    columns:
        id              - topping id;
        topping_name    - name of the topping;
    """

    # database tablename and column setup
    __tablename__ = 'toppings'
    id = db.Column(db.Integer, primary_key=True)
    topping_name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        """
        returns the representation of the Topping class
        """

        return self.topping_name


class NonPizza(db.Model):
    """
    The NonPizza Class defines a non-pizza and is based of db.Model

    tablename: non-pizzas

    columns:
        id          - non-pizza id;
        type_name   - non-pizza type;
        name        - name of non-pizza;
        size        - size of non-pizza;
        cost        - cost of non-pizza;
        product     - products associated with this non-pizza;
    """

    # database tablename and column setup
    __tablename__ = 'non-pizzas'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String, nullable=False)
    size = db.Column(db.String(128), nullable=True)
    cost = db.Column(db.Float, nullable=True)
    product = db.relationship("Product")

    def __repr__(self):
        """
        returns the representation of the NonPizza class
        """

        if self.size:
            return f"{self.type_name} - {self.name} ({self.size})"
        return f"{self.type_name} - {self.name}"


class Product(db.Model):
    """
    The Product Class defines a product and is based of db.Model

    tablename: products

    columns:
        id              - product id;
        pizza_id        - id of the pizza associated with this product;
        nonpizza_id     - id of the non-pizza associated with this product;
        pizza           - pizza associated with this product;
        toppings        - toppings associated with this product;
        nonpizza        - non-pizza associated with this product;
        extra_cheese    - return true if extra cheese;
        orderitem       - orderitems associated with this product;

    methods:
        get_item - gets item of this product;
    """

    # database tablename and column setup
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    nonpizza_id = db.Column(db.Integer, db.ForeignKey('non-pizzas.id'))
    pizza = db.relationship("Pizza", uselist=False)
    toppings = db.relationship("Topping", secondary=toppings)
    nonpizza = db.relationship("NonPizza", uselist=False)
    extra_cheese = db.Column(db.Boolean, default=False)
    orderitem = db.relationship("OrderItem", uselist=False)

    def get_item(self):
        """
        gets the item associated with this product

        this can be done because either of the **_id's must be None/null
        return none if both are none
        """

        if self.pizza_id:
            return self.pizza
        elif self.nonpizza_id:
            return self.nonpizza
        else:
            return None

    def __repr__(self):
        """
        returns the representation of the Product class
        """

        if self.pizza_id:
            if len(self.toppings) > 0:
                return f"{self.pizza} {self.toppings}"
            return f"{self.pizza}"
        elif self.nonpizza_id and self.extra_cheese:
            return f"{self.nonpizza} extra cheese"
        elif self.nonpizza_id:
            return f"{self.nonpizza}"


class OrderItem(db.Model):
    """
    The OrderItem Class defines a order-item and is based of db.Model

    tablename: order-items

    columns:
        id              - order-item id;
        quantity        - quantity of this product;
        created_date    - date order-item was created;
        order_id        - order id associated with this order-item;
        order           - order associated with this order-item;
        product_id      - product id associated with this order-item;
        product         - product asssociated with this order-item;

    methods:
        cost - gets the cost for this order-item;
    """

    # database tablename and column setup
    __tablename__ = 'order-items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.Date, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship("Order")
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship("Product", uselist=False)

    def cost(self):
        """
        return the cost of this order-item

        add $.50 if extra cheese is requested
        """

        if self.product.extra_cheese:
            return self.quantity * (self.product.get_item().cost + .5)
        return self.quantity * self.product.get_item().cost

    def __repr__(self):
        """
        returns the representation of the OrderItem class
        """

        return f"{self.quantity} x {self.product}"


class Order(db.Model):
    """
    The Order Class defines a order and is based of db.Model

    tablename: orders

    columns:
        id              - order id;
        user_id         - id of user associated with this order;
        user            - user associated with this order;
        created_date    - date this order was created;
        orderitem       - orderitems associated with this order;
        checkedout      - true if order is payed and false if order is in cart;

    methods:
        item_number     - returns the number of items in this order;
        order_details   - returns the order details;
    """

    # database tablename and column setup
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User")
    created_date = db.Column(db.Date, nullable=False)
    orderitem = db.relationship("OrderItem")
    checkedout = db.Column(db.Boolean, default=False)

    def item_number(self):
        """
        return the number of items in cart
        """

        item_number = 0
        for item in self.orderitem:
            item_number += item.quantity

        return item_number

    def order_details(self):
        """
        return order details in a dictionary

        values:
            user    - user of the order;
            order   - order self;
            items   - all items in the order;
        """

        # create empty dictionary
        order_details = dict()

        # add user and order to dict
        order_details["user"] = self.user
        order_details["order"] = self

        # add all orderitems of this order into the items list
        order_details["items"] = []

        for item in self.orderitem:
            order_details["items"].append(item)

        return order_details

    def __repr__(self):
        """
        returns the representation of the Order class
        """

        return f"{self.user} - OrderId: {self.id}"


@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    """
    listens for a change in the password of a user
    if called it hashes the new password (if password is changed)

    references:
        https://stackoverflow.com/a/57100627
    """

    if value != oldvalue:
        return s.hash_psswd(value)
    return value
