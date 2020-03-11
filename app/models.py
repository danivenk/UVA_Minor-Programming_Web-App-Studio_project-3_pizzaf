from flask_sqlalchemy import SQLAlchemy
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

    def is_authenticated(self, usrname, passwd):
        if usrname == self.username and s.compare_hash(self.password, passwd):
            return True
        return False

    def is_active(self):
        return True

    def is_anomynous(self):
        return False

    def get_id(self):
        return self.username
