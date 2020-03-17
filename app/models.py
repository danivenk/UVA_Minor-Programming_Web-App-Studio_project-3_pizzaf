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

    def get_id(self):
        return self.id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False


class AnonymousUser(AnonymousUserMixin):
    @property
    def admin(self):
        return False


class Pizza(db.Model):
    __tablename__ = 'Pizza'
    id = db.Column(db.Integer, primary_key=True)
    pizzatype = db.Column(db.String(128), nullable=False)
    size = db.Column(db.String(128), nullable=False)
    toppings = db.Column(db.Integer, nullable=True)
    cost = db.Column(db.Float, nullable=True)

    def __repr__(self):
        if self.toppings == 0:
            return f"{self.pizzatype} ({self.size}): cheese topping only"
        elif self.toppings == 1:
            return f"{self.pizzatype} ({self.size}): {self.toppings} topping"
        elif self.toppings == 5:
            return f"{self.pizzatype} ({self.size}): min {self.toppings} " \
                    "toppings and maximum 8"
        return f"{self.pizzatype} ({self.size}): {self.toppings} toppings"


class NonPizza(db.Model):
    __tablename__ = 'Non-Pizza'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String, nullable=False)
    size = db.Column(db.String(128), nullable=True)
    cost = db.Column(db.Float, nullable=True)
    extras = db.relationship("Extra", backref="Non-Pizza")

    def __repr__(self):
        if self.size:
            return f"{self.type_name} - {self.name} ({self.size})"
        return f"{self.type_name} - {self.name}"


class Topping(db.Model):
    __tablename__ = 'Topping'
    id = db.Column(db.Integer, primary_key=True)
    topping_name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return self.topping_name


class Extra(db.Model):
    __tablename__ = 'Extra'
    id = db.Column(db.Integer, primary_key=True)
    extra = db.Column(db.String(128), nullable=True)
    cost = db.Column(db.Float, nullable=True)
    allowed_on = db.relationship("NonPizza", backref="Extra")
    nonpizza_id = db.Column(db.Integer, db.ForeignKey('Non-Pizza.id'))

    def __repr__(self):
        return self.extra


@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    """
    used soluting from this: https://stackoverflow.com/a/57100627
    """

    if value != oldvalue:
        return s.hash_psswd(value)
    return value


@event.listens_for(Extra.allowed_on, 'set', retval=True)
def extra_allowed_on(target, value, oldvalue, initiator):
    """
    used soluting from this: https://stackoverflow.com/a/57100627
    """

    print(type(value))

    return value
