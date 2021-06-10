from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from .models import Materials, Note, User, Student, Course, Teacher, Student_ids, Attendance, Array_ids, Group, Group_student_id
from . import db
from functools import wraps
import json
from datetime import date, datetime
from .forms import NoticeForm, UpdateAccountForm, Change_password
import os
import secrets
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import time


views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    basedir = os.path.abspath(os.path.dirname(__file__))
    picture_path = os.path.join(basedir, 'static/img', picture_fn)
    print(picture_path)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def validate_course(course_name):
    course = Course.query.filter_by(course_name=course_name).first()
    if course:
        if current_user.user_type == 'p':
            teacher = current_user.teacher[0]
            courses = teacher.courses
            if course in courses:
                return True
            else:
                return False
        else:
            student = current_user.student[0]
            courses_ids = student.courses
            for i in courses_ids:
                temp_course = Course.query.get(i.course_id)
                if course.id == temp_course.id:
                    return True
            return False

    else:
        return False


def get_attendance():
    student = current_user.student[0]
    courses_list = []
    total_courses = Course.query.all()
    for course in total_courses:
        student_ids = course.student_ids
        for j in student_ids:
            if j.student_id == student.id:
                courses_list.append(course)
    attendance_percentages = {}
    for course in courses_list:
        count = 0
        present = 0
        for day in course.attendance:
            if day.student_id == student.id:
                count += 1
                if day.present_status:
                    present += 1
        if count == 0:
            attendance_percentages[course] = 0
        else:
            attendance_percentages[course] = int((present/count)*100)
    return attendance_percentages


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


@views.route('/student_info', methods=['GET', 'POST'])
@login_required
@require_role('s')
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
                              section=section, semester=sem, user_id=current_user.id, user_name=current_user.first_name)
            db.session.add(student)
            db.session.commit()
            flash('Information updated sucessfully', category="success")
            return redirect(url_for('views.home'))
    return render_template('extra_info.html', user=current_user)


@views.route('/profile')
@login_required
def profile():
    image_file = url_for('static', filename='img/' + current_user.profile_pic)
    if current_user.user_type == 's':
        attendance_percentages = get_attendance()
        colors = ['primary', 'danger', 'success', 'warning', 'info']
        return render_template('student_profile.html', user=current_user, image_file=image_file, attendance_percentages=attendance_percentages, colors=colors)
    elif current_user.user_type == 'p':
        return render_template('teacher_profile.html', user=current_user, image_file=image_file)
    elif current_user.user_type == 'a':
        return render_template('admin.html', user=current_user, image_file=image_file)


@views.route('/addpost', methods=['GET', 'POST'])
@login_required
@require_role(role="p")
def addpost():
    form = NoticeForm()
    if form.validate_on_submit():
        title = form.title.data
        note = form.content.data
        print(note)
        sections = {'a': False, 'b': False, 'c': False, 'd': False}
        branchs = {'cse': False, 'it': False, 'mech': False,
                   'ece': False, 'eee': False, 'civil': False}
        years = {'1': False, '2': False, '3': False, '4': False}

        teacher_status = request.form.get("teacher")
        flag = False
        if teacher_status != None:
            flag = True

        section_count = 0
        year_count = 0
        branch_count = 0
        for section in sections:
            temp = request.form.get(section)
            if temp != None:
                sections[section] = True
                section_count += 1
        for year in years:
            temp = request.form.get(year)
            if temp != None:
                years[year] = True
                year_count += 1
        for branch in branchs:
            temp = request.form.get(branch)
            if temp != None:
                branchs[branch] = True
                branch_count += 1
        flag3 = True
        if branch_count == 0 and year_count == 0 and section_count == 0 and not flag:
            flag3 = False
            flash("Please select atleast one branch", "error")
        if not flag:
            if section_count == 0:
                flag3 = False
                flash("Please select atleast one section", "error")

            if year_count == 0:
                flag3 = False
                flash("Please select atleast one year", "error")

            if branch_count == 0:
                flag3 = False
                flash("please select atleast one branch", "error")
        if flag:
            flag2 = False
            if branch_count != 0 or year_count != 0 or section_count != 0:
                flag2 = True

            if section_count == 0 and flag2:
                flag3 = False
                flash("Please select atleast one section", "error")

            if year_count == 0 and flag2:
                flag3 = False
                flash("Please select atleast one year", "error")

            if branch_count == 0 and flag2:
                flag3 = False
                flash("please select atleast one branch", "error")

        if len(note) < 1:
            flag3 = False
            flash("Note is too short!", category="error")
        if flag3:
            notice = Note(data=note, user_id=current_user.id,
                          user_name=current_user.first_name, title=title, notice_type=current_user.user_type)
            db.session.add(notice)
            db.session.commit()
            students = Student.query.all()
            print(notice.data)
            for student in students:
                if sections[student.section] and branchs[student.branch] and years[str(student.year)]:
                    array_ids = Array_ids(
                        note_id=notice.id, user_id=student.user_id)
                    db.session.add(array_ids)
                    db.session.commit()
            if flag:
                teachers = Teacher.query.all()
                current_teacher = current_user.teacher[0]
                for teacher in teachers:
                    if teacher.id != current_teacher.id:
                        array_ids = Array_ids(
                            note_id=notice.id, user_id=teacher.user_id)
                        db.session.add(array_ids)
                        db.session.commit()

            flash('Note added!', category='success')
        else:
            flash("Retry some error occured", category="success")
    return render_template("addnotice.html", user=current_user, form=form)


'''
@views.route('/add_course', methods=['GET', 'POST'])
@login_required
@require_role(role='p')
def add_course():
    if request.method == 'POST':
        branch = request.form.get('branch')
        year = int(request.form.get('year'))
        section = request.form.get('section')
        subject = request.form.get('subject')
        if len(subject) <= 0:
            flash("Please Enter the subject", category="error")
        else:
            teacher = current_user.teacher[0]
            course = Course(subject=subject, branch=branch,
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
    return render_template('addcourse.html', user=current_user)
'''

'''
@views.route('/courses')
@login_required
def courses():
    student = current_user.student[0]
    courses_ids = student.courses
    courses_list = []
    for i in courses_ids:
        courses_list.append(Course.query.get(i.course_id))

    return render_template("courses.html", user=current_user, Teacher=Teacher, User=User, courses_list=courses_list)
'''


@views.route('/classes')
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


@views.route('/courses')
@login_required
def courses():
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


@views.route('/course/<course>/take_attendance', methods=['GET', 'POST'])
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


@views.route('/courses/<course_name>', methods=['GET', 'POST'])
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


@views.route('/attendance')
@login_required
@require_role('s')
def attendance():
    attendance_percentages = get_attendance()
    values = attendance_percentages.values()
    total = sum(values)//len(values)
    return render_template("progress.html", user=current_user, attendance_percentages=attendance_percentages, total=total)


@views.route('/course/<course_name>/attendance')
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


@views.route('/create_group', methods=['GET', 'POST'])
@login_required
@require_role('p')
def create_group():
    if request.method == 'POST':
        regnos = request.form.get("regnos")
        flag2 = True
        group_name = request.form.get('name')
        print(regnos)
        if len(group_name) == 0:
            flash("Please enter group name", category="error")
            flag2 = False
        if len(regnos) == 0:
            flag2 = False
            flash("Please enter register numbers", category="error")
        regnos = regnos.split(',')
        if len(regnos) == 0:
            flag2 = False
            flash('Please enter register numbers seperated by commas',
                  category="error")
        students = []
        total_students = Student.query.all()
        for regno in regnos:
            flag = False
            for student in total_students:
                if student.regno == regno:
                    students.append(student)
                    flag = True
            if not flag:
                flag2 = False
                flash("Please enetr valid Register number", category="error")
                break
        if flag2:
            teacher = current_user.teacher[0]
            group = Group(teacher_id=teacher.id, group_name=group_name)
            db.session.add(group)
            db.session.commit()
            for student in students:
                group_student_id = Group_student_id(
                    group_id=group.id, student_id=student.id)
                db.session.add(group_student_id)
                db.session.commit()
            flash("Group created sucessfully", category="success")

    return render_template("create_group.html", user=current_user)


@views.route('/groups')
@login_required
@require_role('s')
def groups():
    groups_list = []
    student = current_user.student[0]
    teachers = {}
    student_ids = Group_student_id.query.all()
    for student_id in student_ids:
        if student_id.student_id == student.id:
            group = Group.query.get(student_id.group_id)
            groups_list.append(group)
            teacher = Teacher.query.get(group.teacher_id)
            teachers[group.id] = teacher.user_name
    return render_template("groups.html", user=current_user, groups=groups_list, teachers=teachers)


@views.route('/profile/edit', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_pic = picture_file

        dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d')
        gender = request.form.get('gender')
        current_user.first_name = form.username.data
        current_user.email = form.email.data
        current_user.gender = gender
        current_user.dob = dob
        db.session.commit()
    elif request.method == 'GET':
        form.username.data = current_user.first_name
        form.email.data = current_user.email
        form.mobile.data = current_user.mobile
    image_file = url_for(
        'static', filename='img/' + current_user.profile_pic)
    return render_template("edit_profile.html", user=current_user, form=form, image_file=image_file)


@views.route('/change_password', methods=['POST', 'GET'])
@login_required
def change_password():
    form = Change_password()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.password.data):
            current_user.password = generate_password_hash(
                form.new_password.data, method='sha256')
            db.session.commit()
            flash("Password Changed Sucessfully", category="success")
        else:
            flash("Incorrect password, try again.", category="error")
    return render_template("change_password.html", user=current_user, form=form)


@views.route('/forget_password', methods=['POST', 'GET'])
def forget_password():
    pass


@views.route('/course/<course_name>/add_material', methods=['GET', 'POST'])
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


@ views.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file attached in request', category='error')
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', category='error')
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            basedir = os.path.abspath(os.path.dirname(__file__))
            file.save(os.path.join(basedir, 'static/uploads', filename))
            flash("File uploaded succesfully", category='success')
        else:
            flash('File not allowed', category='error')
    return render_template('test.html', user=current_user,)


@ views.route('/download/<filename>')
def uploaded_file(filename):
    basedir = os.path.abspath(os.path.dirname(__file__))
    return send_from_directory(os.path.join(basedir, 'static/uploads'), filename, as_attachment=True)
