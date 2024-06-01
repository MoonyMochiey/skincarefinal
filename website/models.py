from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func



class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')

class SkincareFormEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cleanser = db.Column(db.String(100))
    toner = db.Column(db.String(100))
    moisturizer = db.Column(db.String(100))
    serum = db.Column(db.String(100))
    sunscreen = db.Column(db.String(100))

class Producte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Text)
    ingredients = db.Column(db.Text)
    target = db.Column(db.String(100))



    