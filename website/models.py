from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #user_name = db.Column(db.String(150), db.ForeignKey('user.first_name'))


'''
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
'''

'''
class Student(db.Model):
    regno = db.Column(db.String(10), unique=True)
    branch = db.Column(db.String(20))
    section = db.Column(db.String(1))
    year = db.Column(db.Integer)
    semester = db.Column(db.Integer)
'''


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    user_type = db.Column(db.String(1))
    notes = db.relationship('Note')

class Student(User):
    regno = db.Column(db.String(10), unique=True)
    branch = db.Column(db.String(20))
    section = db.Column(db.String(1))
    year = db.Column(db.Integer)
    semester = db.Column(db.Integer)
