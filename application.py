import os

from flask import Flask, render_template, request
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import *

# Configure Flask app
app = Flask(__name__)

# Configure database
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Configure session, use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure migrations
Migrate(app, db)

@app.route("/")
def index():
    return f"Pinocchio's: TODO"
