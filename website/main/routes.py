from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from ..models import Materials, Note, User, Student, Course, Teacher, Student_ids, Attendance, Array_ids, Group, Group_student_id
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

    if current_user.user_type.lower() == 's':
        return render_template("home.html", user=current_user, notes=user_notes)
    elif current_user.user_type.lower() == 'p':
        return render_template("teacher_home.html", user=current_user, notes=user_notes)
    elif current_user.user_type.lower() == 'a':
        return render_template('admin.html', user=current_user)
    else:
        return redirect(url_for(views.logout))


@ views.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        skills = request.form.getlist('skill[]')
        for value in skills:
            print(value)
        msg = 'New record created successfully'
    return jsonify(msg)


@ views.route('/test2', methods=['GET', 'POST'])
def test2():
    return render_template('test.html')
