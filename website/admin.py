from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.sql.functions import user
from .models import Note, User, Student, Course, Teacher, Student_ids, Attendance, Array_ids, Group, Group_student_id
from . import db
from .views import require_role
from .forms import AddStudent, AddTeacher, AddCourse
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

admin = Blueprint('admin', __name__)


@admin.route('/add_student', methods=['GET', 'POST'])
@login_required
@require_role('a')
def add_student():
    form = AddStudent()
    if form.validate_on_submit():
        branch = request.form.get('branch')
        section = request.form.get('section')
        year = request.form.get('year')
        sem = request.form.get('sem')
        dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d')
        gender = request.form.get('gender')
        new_user = User(email=form.email.data, first_name=form.username.data, password=generate_password_hash(
            "1234567", method='sha256'), user_type='s', gender=gender, dob=dob, mobile=int(form.mobile.data))
        db.session.add(new_user)
        db.session.commit()
        student = Student(regno=form.regno.data, branch=branch, year=year,
                          section=section, semester=sem, user_id=new_user.id, user_name=new_user.first_name)
        db.session.add(student)
        db.session.commit()
        flash("Student Added!", category='success')
    return render_template('add_student.html', user=current_user, form=form, date=date.today())


@admin.route('/add_teacher', methods=['GET', 'POST'])
@login_required
@require_role('a')
def add_teacher():
    form = AddTeacher()
    if form.validate_on_submit():
        dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d')
        gender = request.form.get('gender')
        new_user = User(email=form.email.data, first_name=form.username.data, password=generate_password_hash(
            "1234567", method='sha256'), user_type='p', gender=gender, dob=dob, mobile=int(form.mobile.data))
        db.session.add(new_user)
        db.session.commit()
        teacher = Teacher(user_id=new_user.id, user_name=new_user.first_name,
                          teacher_regno=form.teacher_id.data)
        db.session.add(teacher)
        db.session.commit()
        flash("Teacher Added!", category='success')
    return render_template('add_teacher.html', user=current_user, form=form, date=date.today())


@admin.route('/add_course', methods=['GET', 'POST'])
@login_required
@require_role('a')
def add_course():
    form = AddCourse()
    if form.validate_on_submit():
        branch = request.form.get('branch')
        year = int(request.form.get('year'))
        section = request.form.get('section')
        teacher = Teacher.query.filter_by(
            teacher_regno=form.teacher_id.data).first()
        if teacher:
            course = Course(subject=form.subject.data, branch=branch,
                            year=year, section=section, teacher_id=teacher.id)
            db.session.add(course)
            db.session.commit()
            students = Student.query.all()
            for student in students:
                if student.branch == branch and student.section == section and student.year == year:
                    student_ids = Student_ids(
                        course_id=course.id, student_id=student.id)
                    db.session.add(student_ids)
                    db.session.commit()
            flash('Information added sucessfully', category="success")
        else:
            flash('Teacher id is not present', category='error')
    return render_template('addcourse.html', user=current_user, form=form)
