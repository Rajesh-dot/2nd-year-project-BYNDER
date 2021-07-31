import PIL
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from flask_login import login_required, current_user
from ..models import Lecture, Materials, User, Student, Course, Teacher, Attendance, Note, Array_ids
from website import db
from website.main.utils import require_role
from datetime import date
import os
from werkzeug.utils import secure_filename
import time
from .utils import validate_course, get_attendance, allowed_file, get_attend_info

courses = Blueprint('courses', __name__)


@ courses.route('/download/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config["FILE_UPLOADS"], filename, as_attachment=True)


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
                    file.save(os.path.join(
                        current_app.config["FILE_UPLOADS"], filename))
                    material = Materials(
                        teacher_id=teacher.id, course_id=course.id, material=filename)
                    db.session.add(material)
                    db.session.commit()
                    flash("File uploaded succesfully", category='success')
                else:
                    flash('File not allowed', category='error')
            return redirect(url_for('courses.course_home', course_name=course_name))
        else:
            flash("No permission", category="error")
            return redirect(url_for('courses.course_home', course_name=course_name))
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


@courses.route('/courses/<course_name>/', methods=['GET', 'POST'])
@login_required
def course_home(course_name):
    if validate_course(course_name):
        course = Course.query.filter_by(course_name=course_name).first()
        teacher = Teacher.query.get(course.teacher_id)
        name = teacher.user_name
        materials = course.materials
        materials_sizes = {}
        times = {}
        for i in materials:
            path = os.path.join(current_app.config["FILE_UPLOADS"], i.material)
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


@courses.route('/course/<course>/take_attendance/', methods=['GET', 'POST'])
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
        lecture = Lecture(course_id=course.id)
        db.session.add(lecture)
        db.session.commit()
        for student in students_list:
            present_status = request.form.get(str(student.id))
            if present_status != None:
                attendance = Attendance(
                    present_status=True, lecture_id=lecture.id, student_id=student.id)
            else:
                attendance = Attendance(
                    present_status=False, lecture_id=lecture.id, student_id=student.id)
                notice = Note(data="You are marked as absent for "+course_name, user_id=1,
                          user_name="Admin", title="Absent", notice_type='a')
                db.session.add(notice)
                db.session.commit()
                array_ids = Array_ids(
                        note_id=notice.id, user_id=student.user_id)
                db.session.add(array_ids)
                db.session.commit()
            db.session.add(attendance)
            db.session.commit()

    return render_template("attendance.html", user=current_user, students_list=students_list, course=course, date=date.today())


@courses.route('/course/<course>/lectures/', methods=['GET', 'POST'])
@login_required
@require_role('p')
def lectures_info(course):
    course_name = course
    course = Course.query.filter_by(course_name=course_name).first()
    if course:
        lectures_info = []
        lectures = course.lecture
        for lecture in lectures:
            info = get_attend_info(lecture)
            present,absent=len(info['presentees']),len(info['absentees'])
            lectures_info.append({"lecture":lecture,"date":lecture.date.strftime("%m/%d/%Y, %H:%M:%S"),"present":present,"absent":absent})
        return render_template('lectures.html',user=current_user,lectures_info=lectures_info,course=course)
    else:
        return f"<h1>404 NOT FOUND</h>"

@courses.route('/course/<course>/<id>/info', methods=['GET', 'POST'])
@login_required
@require_role('p')
def lecture_present_info(course, id):
    course_name = course
    course = Course.query.filter_by(course_name=course_name).first()
    lecture = Lecture.query.get(id)
    if course!=None and lecture!=None: #and lecture.subject==course.course_name
        info = get_attend_info(lecture)
        present_ids,absent_ids=info['presentees'],info['absentees']
        present_data=[]
        absent_data=[]
        for index,idx in enumerate(present_ids):
            student=Student.query.get(idx)
            present_data.append((index+1,{'roll_no':student.regno,'name':student.user_name}))
        for index,idx in enumerate(absent_ids):
            student=Student.query.get(idx)
            absent_data.append((index+1,{'roll_no':student.regno,'name':student.user_name}))
        return render_template('lecture_info.html',user=current_user,present_data=present_data,absent_data=absent_data)
    else:
        return f"<h1>404 NOT FOUND</h>"

@courses.route('/course/<course>/<id>/edit', methods=['GET', 'POST'])
@login_required
@require_role('p')
def edit_lecture(course, id):
    course_name = course
    course = Course.query.filter_by(course_name=course_name).first()
    lecture = Lecture.query.get(id)
    if course!=None and lecture!=None:
        students_info=[]
        attendance=lecture.attendance
        student_attend_map={}
        for attend in attendance:
            student = Student.query.get(attend.student_id)
            student_attend_map[student.regno] = attend
            students_info.append({'regno':student.regno,'name':student.user_name,'present_status':attend.present_status,'attend_id':attend.id})
        if request.method=='POST':
            for student_regno in student_attend_map:
                present_status = request.form.get(str(student_regno))
                if present_status != None:
                    attend = student_attend_map[student_regno]
                    attend.present_status = True
                else:
                    attend = student_attend_map[student_regno]
                    attend.present_status = False
                db.session.commit()
            flash("Updated Sucessfull",category='success')
            return redirect(url_for('courses.lectures_info',course=course_name))

        return render_template('edit_lecture.html',user=current_user,students_info=students_info,course=course, date=lecture.date)
    else:
        return f"<h1>404 NOT FOUND</h>"
