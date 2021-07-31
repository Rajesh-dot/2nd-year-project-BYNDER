from sqlalchemy.orm import backref
from . import db
from flask_login import UserMixin
from flask_security import RoleMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    data = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_ids = db.relationship("Array_ids")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    notice_type = db.Column(db.String(1))
    user_name = db.Column(db.String(150))


class Array_ids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    user_type = db.Column(db.String(1), nullable=False)
    notes = db.relationship('Note', backref='author', lazy=True)
    array_ids = db.relationship('Array_ids')
    student = db.relationship('Student', backref='user')
    teacher = db.relationship('Teacher', backref='user')
    mobile = db.Column(db.Integer, nullable=False)
    profile_pic = db.Column(
        db.String(150), nullable=False, default="default.jpg")
    dob = db.Column(db.DateTime(timezone=True), nullable=False)
    gender = db.Column(db.String(1), nullable=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regno = db.Column(db.String(10), unique=True, nullable=False)
    branch = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(1), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    attendance = db.relationship('Attendance')
    courses = db.relationship('Student_ids')
    groups = db.relationship('Group_student_id')
    user_name = db.Column(db.String(150))


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_regno = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_name = db.Column(db.String(150))
    courses = db.relationship('Course')
    groups = db.relationship('Group')
    materials = db.relationship('Materials')


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(20))
    section = db.Column(db.String(1))
    year = db.Column(db.Integer)
    subject = db.Column(db.String(50))
    course_name = db.Column(db.String(100))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    student_ids = db.relationship('Student_ids')
    #attendance = db.relationship('Attendance')
    lecture = db.relationship('Lecture')
    materials = db.relationship('Materials')


class Student_ids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))


class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    #absentees_count = db.Column(db.Integer)
    #presentees_count = db.Column(db.Integer)
    #course_name = db.Column(db.String(100))
    attendance = db.relationship('Attendance')


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    present_status = db.Column(db.Boolean, nullable=False)
    #course_id = db.Column(db.Integer)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(30), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        'teacher.id'), nullable=False)
    student_ids = db.relationship('Group_student_id')
    notices = db.relationship('Group_Notices')


class Group_student_id(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))


class Materials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    material = db.Column(db.String(150), nullable=False)


class Group_Notices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    data = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.String(50),nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))



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
