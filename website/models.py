from . import db
from flask_login import UserMixin
from flask_security import RoleMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_ids = db.relationship("Array_ids")
    #user_name = db.Column(db.String(150), db.ForeignKey('user.first_name'))

class Array_ids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    user_type = db.Column(db.String(1))
    student = db.relationship('Student')
    teacher = db.relationship('Teacher')


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regno = db.Column(db.String(10), unique=True)
    branch = db.Column(db.String(20))
    section = db.Column(db.String(1))
    year = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    courses = db.relationship('Course')
    attendance = db.relationship('Attendance')



class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    courses = db.relationship('Course')


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(20))
    section = db.Column(db.String(1))
    year = db.Column(db.Integer)
    subject = db.Column(db.String(50))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    attendance = db.relationship('Attendance')


class Attendance(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    present_status = db.Column(db.Boolean)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))


'''
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    user_type = db.Column(db.String(1))
    notes = db.relationship('Note')
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def has_role(self, role_name):
        """Does this user have this permission?"""
        my_role = Role.query.filter_by(name=role_name).all()
        print(my_role, self.roles)
        for role in my_role:
            if role in self.roles:
                return True
            else:
                return False
'''

'''
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    user_type = db.Column(db.String(1))
    notes = db.relationship('Note')

    __mapper_args__ = {
        'polymorphic_identity': 'employee',
        'polymorphic_on': user_type
    }
'''


'''
class Student(User):
    __tablename__ = 'student'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    regno = db.Column(db.String(10), unique=True)
    branch = db.Column(db.String(20))
    section = db.Column(db.String(1))
    year = db.Column(db.Integer)
    semester = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }


class Teacher(User):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'teacher',
    }


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
'''
