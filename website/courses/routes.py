from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from ..models import Materials, User, Student, Course, Teacher, Attendance
from website import db
from website.main.utils import require_role
from datetime import date
import os
from werkzeug.utils import secure_filename
import time
from .utils import validate_course, get_attendance, allowed_file

courses = Blueprint('courses', __name__)


@ courses.route('/download/<filename>')
def uploaded_file(filename):
    basedir = os.path.abspath(os.path.dirname(__file__))
    return send_from_directory(os.path.join(basedir, 'static/uploads'), filename, as_attachment=True)


@courses.route('/course/<course_name>/add_material', methods=['GET', 'POST'])
@login_required
@require_role('p')
def add_material(course_name):
    course_name = course_name
    course = Course.query.filter_by(course_name=course_name).first()
    if course:
        teacher = current_user.teacher[0]
        if course in teacher.courses:
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('No file attached in request', category='error')
                file = request.files['file']
                if file.filename == '':
                    flash('No file selected', category='error')
                elif file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    basedir = os.path.abspath(os.path.dirname(__file__))
                    file.save(os.path.join(
                        basedir, 'static/uploads', filename))
                    material = Materials(
                        teacher_id=teacher.id, course_id=course.id, material=filename)
                    db.session.add(material)
                    db.session.commit()
                    flash("File uploaded succesfully", category='success')
                else:
                    flash('File not allowed', category='error')
            return redirect(url_for('views.course_home', course_name=course_name))
        else:
            flash("No permission", category="error")
            return redirect(url_for('views.course_home', course_name=course_name))
    else:
        return f"<h1>404 NOT FOUND</h>"


@courses.route('/course/<course_name>/attendance')
@login_required
@require_role('s')
def course_attendance(course_name):
    if validate_course(course_name):
        course = Course.query.filter_by(course_name=course_name).first()
        attendance_percentages = get_attendance()[course]
        teacher = Teacher.query.get(course.teacher_id)
        name = teacher.user_name
        return render_template("course_attendance.html", user=current_user, attendance_percentages=attendance_percentages, course=course, name=name)
    else:
        f"<h1>404 NOT FOUND</h1>"


@courses.route('/courses/<course_name>', methods=['GET', 'POST'])
@login_required
def course_home(course_name):
    if validate_course(course_name):
        course = Course.query.filter_by(course_name=course_name).first()
        teacher = Teacher.query.get(course.teacher_id)
        name = teacher.user_name
        materials = course.materials
        materials_sizes = {}
        basedir = os.path.abspath(os.path.dirname(__file__))
        times = {}
        for i in materials:
            path = os.path.join(basedir, 'static/uploads', i.material)
            materials_sizes[i] = os.path.getsize(path)
            times[i] = time.ctime(os.path.getctime(path))
        materials.reverse()
        return render_template('classes.html', user=current_user, materials=materials, name=name, course=course, sizes=materials_sizes, times=times)
    else:
        return f"<h1>404 NOT FOUND</h>"


@courses.route('/classes')
@login_required
@require_role('p')
def classes():
    teacher = current_user.teacher[0]
    course_names = {}
    for course in teacher.courses:
        a = course.subject + " - " + \
            str(course.year) + " Yr " + course.branch.upper() + \
            " Sec " + course.section.upper()
        course_names[course.course_name] = a
    return render_template('courses.html', user=current_user, course_names=course_names)


@courses.route('/courses')
@login_required
def get_courses():
    if current_user.user_type == 'p':
        teacher = current_user.teacher[0]
        course_names = {}
        for course in teacher.courses:
            a = course.subject + " - " + \
                str(course.year) + " Yr " + course.branch.upper() + \
                " Sec " + course.section.upper()
            course_names[course.course_name] = a
    else:
        student = current_user.student[0]
        courses_ids = student.courses
        course_names = {}
        for i in courses_ids:
            course = Course.query.get(i.course_id)
            a = course.subject + " - " + \
                str(course.year) + " Yr " + course.branch.upper() + \
                " Sec " + course.section.upper()
            course_names[course.course_name] = a
    return render_template('courses.html', user=current_user, course_names=course_names)


@courses.route('/course/<course>/take_attendance', methods=['GET', 'POST'])
@login_required
@require_role('p')
def subject(course):
    course_name = course
    course = Course.query.filter_by(course_name=course_name).first()
    if course:
        year = course.year
        branch = course.branch
        section = course.section
    else:
        return f"<h1>404 NOT FOUND</h>"

    teacher = current_user.teacher[0]
    if teacher.id != course.teacher_id:
        return redirect("/")

    students_list = []
    students = Student.query.all()
    for student in students:
        if student.branch == branch and student.section == section and student.year == year:
            students_list.append(student)
    if request.method == 'POST':
        # date = request.form.get("date")
        for student in students_list:
            present_status = request.form.get(str(student.id))
            if present_status != None:
                attendance = Attendance(
                    present_status=True, course_id=course.id, student_id=student.id)
            else:
                attendance = Attendance(
                    present_status=False, course_id=course.id, student_id=student.id)
            db.session.add(attendance)
            db.session.commit()

    return render_template("attendance.html", user=current_user, students_list=students_list, course_name=course_name, date=date.today())
