from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from ..models import Lecture, Materials, Note, User, Student, Course, Teacher, Student_ids, Attendance, Array_ids, Group, Group_student_id
from website import db
from functools import wraps
import json
from datetime import date, datetime
import os
import secrets
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import time
from .utils import get_attend_info


views = Blueprint('views', __name__)


def require_role(role):
    """make sure user has this role"""
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            if not current_user.user_type == role:
                flash("No Permission", category="error")
                return redirect("/")
            else:
                return func(*args, **kwargs)
        return wrapped_function
    return decorator


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    user_notes = []
    notes = Note.query.all()
    for note in notes:
        user_ids = note.user_ids
        for user_id in user_ids:
            if current_user.id == user_id.user_id:
                user_notes.append(note)
        if note.user_id == current_user.id:
            user_notes.append(note)
    user_notes.reverse()

    if current_user.user_type.lower() == 's' or current_user.user_type.lower() == 'p':
        print(current_user.id)
        return render_template("home.html", user=current_user, notes=user_notes)
    elif current_user.user_type.lower() == 'a':
        print(current_user.id)
        return render_template('admin.html', user=current_user)
    else:
        return redirect(url_for(views.logout))


'''
@ views.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        skills = request.form.getlist('skill[]')
        for value in skills:
            print(value)
        msg = 'New record created successfully'
    return jsonify(msg)
'''


@ views.route('/test', methods=['GET', 'POST'])
def test2():
    student = current_user.student[0]
    courses_list = []
    courses_ids = student.courses
    for course_id in courses_ids:
        courses_list.append(Course.query.get(course_id.course_id))
    lectures_info = [{}]
    for course in courses_list:
        lectures = course.lecture
        for lecture in lectures:
            info = get_attend_info(lecture)
            present,absent=len(info['presentees']),len(info['absentees'])
            lectures_info.append({"lecture":lecture,"date":lecture.date.strftime("%m/%d/%Y, %H:%M:%S"),"present":present,"absent":absent})
        break
    print(lectures_info)
    return render_template('test.html', user=current_user, lectures_info=lectures_info)
