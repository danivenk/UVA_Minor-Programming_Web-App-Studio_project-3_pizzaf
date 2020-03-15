from flask_sqlalchemy import SQLAlchemy, event
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

    def get_id(self):
        return self.id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True


class Pizza(db.Model):
    __tablename__ = 'Pizza'
    id = db.Column(db.Integer, primary_key=True)
    pizzatype = db.Column(db.String(128), nullable=False)
    size = db.Column(db.String(128), nullable=False)
    toppings = db.Column(db.String(1028), nullable=True)
    cost = db.Column(db.Float, nullable=True)


class NonPizza(db.Model):
    __tablename__ = 'Non-Pizza'
    id = db.Column(db.Integer, primary_key=True)
    NPtype = db.Column(db.String(128), nullable=False)
    extras = db.Column(db.String(1028), nullable=True)
    cost = db.Column(db.Float, nullable=True)


@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    """
    used soluting from this: https://stackoverflow.com/a/57100627
    """

    if value != oldvalue:
        return s.hash_psswd(value)
    return value
