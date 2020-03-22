from flask_sqlalchemy import SQLAlchemy, event
from flask_login import AnonymousUserMixin
from functions import security as s

db = SQLAlchemy()


class User(db.Model):
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
        return self.id

    def items_in_cart(self):
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
        return self.first_name + " " + self.last_name


class AnonymousUser(AnonymousUserMixin):
    @property
    def admin(self):
        return False


toppings = db.Table('toppings_association',
                    db.Column('topping_id', db.ForeignKey('toppings.id'),
                              primary_key=True),
                    db.Column('product_id', db.ForeignKey('products.id'),
                              primary_key=True)
                    )


class Pizza(db.Model):
    __tablename__ = 'pizzas'
    id = db.Column(db.Integer, primary_key=True)
    pizzatype = db.Column(db.String(128), nullable=False)
    size = db.Column(db.String(128), nullable=False)
    no_toppings = db.Column(db.Integer, nullable=True)
    cost = db.Column(db.Float, nullable=True)
    orderitem = db.relationship("Product")

    def __repr__(self):
        if self.no_toppings == 0:
            return f"{self.pizzatype} ({self.size}): cheese topping only"
        elif self.no_toppings == 1:
            return f"{self.pizzatype} ({self.size}): {self.no_toppings} " \
                    "topping"
        elif self.no_toppings == 5:
            return f"{self.pizzatype} ({self.size}): min {self.no_toppings} " \
                    "toppings and maximum 8"
        return f"{self.pizzatype} ({self.size}): {self.no_toppings} toppings"


class Topping(db.Model):
    __tablename__ = 'toppings'
    id = db.Column(db.Integer, primary_key=True)
    topping_name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return self.topping_name


class NonPizza(db.Model):
    __tablename__ = 'non-pizzas'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String, nullable=False)
    size = db.Column(db.String(128), nullable=True)
    cost = db.Column(db.Float, nullable=True)
    orderitem = db.relationship("Product")

    def __repr__(self):
        if self.size:
            return f"{self.type_name} - {self.name} ({self.size})"
        return f"{self.type_name} - {self.name}"


class Product(db.Model):
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
        if self.pizza_id:
            return self.pizza
        elif self.nonpizza_id:
            return self.nonpizza
        else:
            return None

    def __repr__(self):
        if self.pizza_id:
            return f"{self.pizza}"
        elif self.nonpizza_id:
            return f"{self.nonpizza}"


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User")
    created_date = db.Column(db.Date, nullable=False)
    orderitem = db.relationship("OrderItem")
    checkedout = db.Column(db.Boolean, default=False)

    def item_number(self):
        item_number = 0
        for item in self.orderitem:
            item_number += item.quantity

        return item_number

    def order_details(self):
        order_details = dict()

        order_details["user"] = self.user

        order_details["items"] = []

        for item in self.orderitem:
            order_details["items"].append(item)

        return order_details

    def __repr__(self):
        return f"{self.user} - OrderId: {self.id}"


class OrderItem(db.Model):
    __tablename__ = 'order-items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.Date, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship("Order")
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship("Product", uselist=False)

    def cost(self):
        return self.quantity * self.product.get_item().cost

    def __repr__(self):
        return f"{self.quantity} x {self.product}"


@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    """
    used soluting from this: https://stackoverflow.com/a/57100627
    """

    if value != oldvalue:
        return s.hash_psswd(value)
    return value
