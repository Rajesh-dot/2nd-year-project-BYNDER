from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, User, Student, Teaching, Teacher
from . import db
from functools import wraps
import json

views = Blueprint('views', __name__)


def require_role(role):
    """make sure user has this role"""
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            if not current_user.user_type == role:
                return redirect("/profile")
            else:
                return func(*args, **kwargs)
        return wrapped_function
    return decorator


@views.route('/', methods=['GET', 'POST'])
@login_required
# @require_role(role="Teacher")
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash("Note is too short!", category="error")
        else:
            # print(current_user.id)
            rows = db.session.query(User).count()
            for i in range(rows+1):
                new_note = Note(data=note, user_id=i)
                db.session.add(new_note)
                db.session.commit()
            flash('Note added!', category='success')
    if current_user.user_type.lower()=='s':
        return render_template("home.html", user=current_user)
    elif current_user.user_type.lower()=='p':
        return render_template("teacher_home.html", user=current_user)


@views.route('/student_info', methods=['GET', 'POST'])
@login_required
def student_info():
    if request.method == 'POST':
        branch = request.form.get('branch')
        sem = request.form.get('sem')
        year = request.form.get('year')
        section = request.form.get('section')
        regno = request.form.get('regno')
        if len(regno) < 10 or len(regno) > 10:
            flash("Invalid Register Number", category="error")
        else:
            student = Student(regno=regno, branch=branch, year=year,
                              section=section, semester=sem, user_id=current_user.id)
            db.session.add(student)
            db.session.commit()
            flash('Information updated sucessfully', category="success")
            return redirect(url_for('views.home'))
    return render_template('extra_info.html', user=current_user)


@views.route('/profile')
@login_required
def user():
    return render_template('user_base.html', user=current_user)


@views.route('/addpost', methods=['GET', 'POST'])
@login_required
def addpost():
    if current_user.user_type.lower()=='s':
        return redirect("/")
    return render_template("addnotice.html",user=current_user)


@views.route('/add_teaching', methods=['GET', 'POST'])
@login_required
def add_teaching():
    if request.method == 'POST':
        branch = request.form.get('branch')
        year = request.form.get('year')
        section = request.form.get('section')
        subject = request.form.get('subject')
        if len(subject) <= 0:
            flash("Please Enter the subject", category="error")
        else:
            teacher = current_user.teacher[0]
            teaching = Teaching(subject=subject, branch=branch, year=year,
                                section=section, teacher_id=teacher.id)
            db.session.add(teaching)
            db.session.commit()
            flash('Information added sucessfully', category="success")
    return render_template('extra_info_teacher.html', user=current_user)


@ views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})


@views.route('/test',methods=['GET','POST'])
def test():
    if request.method=='POST':
        year = request.form.get("year")
        print(year)
        print(type(year))
    return render_template('test.html',user=current_user)
