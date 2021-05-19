from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.sql.functions import user
from .models import Note, User, Student, Course, Teacher, Student_ids, Attendance, Array_ids, Group, Group_student_id
from . import db
from .views import require_role
from .forms import AddStudent
from werkzeug.security import generate_password_hash, check_password_hash

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
        new_user = User(email=form.email.data, first_name=form.username.data, password=generate_password_hash(
            "1234567", method='sha256'), user_type='s')
        db.session.add(new_user)
        db.session.commit()
        student = Student(regno=form.regno.data, branch=branch, year=year,
                          section=section, semester=sem, user_id=new_user.id, user_name=new_user.first_name)
        db.session.add(student)
        db.session.commit()
        flash("Student Added!", category='success')
    return render_template('add_student.html', user=current_user, form=form)


@admin.route('/add_student', methods=['GET', 'POST'])
@login_required
@require_role('a')
def add_teacher():
    pass
