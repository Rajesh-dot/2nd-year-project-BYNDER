from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, User, Student, Course, Teacher, Student_ids, Attendance, Array_ids
from . import db
from functools import wraps
import json
from datetime import date

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
# @require_role(role="Teacher")
def home():
    rows = db.session.query(Note).count()
    notes = []
    for i in range(1,rows+1):
        temp_note = Note.query.get(i)
        user_ids = temp_note.user_ids
        for j in user_ids:
            if current_user.id==j.user_id:
                notes.append(temp_note)
        if temp_note.user_id==current_user.id:
            notes.append(temp_note)

    if current_user.user_type.lower()=='s':
        return render_template("home.html", user=current_user,notes=notes)
    elif current_user.user_type.lower()=='p':
        return render_template("teacher_home.html", user=current_user,notes=notes)


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
                              section=section, semester=sem, user_id=current_user.id)
            db.session.add(student)
            db.session.commit()
            flash('Information updated sucessfully', category="success")
            return redirect(url_for('views.home'))
    return render_template('extra_info.html', user=current_user)


@views.route('/profile')
@login_required
def profile():
    return render_template('user_base.html', user=current_user)


@views.route('/addpost', methods=['GET', 'POST'])
@login_required
@require_role(role="p")
def addpost():
    if request.method == 'POST':
        note = request.form.get('note')
        sections = {'a':False,'b':False,'c':False,'d':False}
        branchs = {'cse':False,'it':False,'mech':False,'ece':False,'eee':False,'civil':False}
        years = {'1':False,'2':False,'3':False,'4':False}

        c=0
        for section in sections:
            temp = request.form.get(section)
            if temp!=None:
                sections[section] = True
                c+=1
        if c==0:
            flash("Please select atleast one section","error")

        c=0
        for year in years:
            temp = request.form.get(year)
            if temp!=None:
                years[year] = True
                c+=1
        if c==0:
            flash("Please select atleast one year","error")

        c=0
        for branch in branchs:
            temp = request.form.get(branch)
            if temp!=None:
                branchs[branch] = True
                c+=1
        if c==0:
            flash("please select atleast one branch","error")

        if len(note) < 1:
            flash("Note is too short!", category="error")
        else:
            # print(current_user.id)
            notice = Note(data=note,user_id=current_user.id)
            db.session.add(notice)
            db.session.commit()
            rows = db.session.query(User).count()
            for i in range(rows+1):
                user = User.query.get(i)
                if user!=None:
                    student = user.student
                    if len(student)!=0:
                        student = student[0]
                        if sections[student.section] and branchs[student.branch] and years[str(student.year)]:
                            array_ids = Array_ids(note_id=notice.id,user_id=user.id)
                            db.session.add(array_ids)
                            db.session.commit()

            flash('Note added!', category='success')
    return render_template("addnotice.html",user=current_user)


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
            course = Course(subject=subject, branch=branch, year=year,section=section, teacher_id=teacher.id)
            db.session.add(course)
            db.session.commit()
            rows = db.session.query(Student).count()
            for i in range(1,rows+1):
                student = Student.query.get(i)
                if student!=None:
                    if student.branch==branch and student.section==section and student.year==year:
                        student_ids = Student_ids(course_id=course.id,student_id=student.id)
                        db.session.add(student_ids)
                        db.session.commit()
            flash('Information added sucessfully', category="success")
    print(db.session.query(Course).count())
    return render_template('extra_info_teacher.html', user=current_user)


@views.route('/courses')
@login_required
@require_role('s')
def courses():
    student = current_user.student[0]
    rows = db.session.query(Course).count()
    courses_list = []
    for i in range(1,rows+1):
        course = Course.query.get(i)
        if course!=None:
            student_ids = course.student_ids
            for j in student_ids:
                if j.student_id==student.id:
                    courses_list.append(course)
    return render_template("courses.html",user=current_user,Teacher=Teacher,User=User,courses_list=courses_list)



@views.route('/classes')
@login_required
@require_role('p')
def classes():
    teacher = current_user.teacher[0]
    course_names = []
    for course in teacher.courses:
        a = course.subject + " - " + str(course.year) + " Yr " + course.branch.upper() + " Sec " + course.section.upper()
        course_names.append(a)
    course_names = list(set(course_names))
    return render_template('classes.html',user=current_user,course_names=course_names)



@views.route('/<course>',methods = ['GET','POST'])
@login_required
@require_role('p')
def subject(course):
    course_name = course
    flag = True
    try:
        values = ['','','','']
        split = [' - ',' Yr ',' Sec ']
        for i in range(3):
            course = course.split(split[i])
            values[i] = course[0]
            course = course[1]
        values[3] = course
    except:
        return f"<h1>404 NOT FOUND</h>"
    
    subject = values[0]
    year = int(values[1])
    branch = values[2].lower()
    section = values[3].lower()

    if year>4 or year<1:
        return f"<h1>404 NOT FOUND</h>"
    
    if branch not in ['cse','it','mech','civil','eee','ece']:
        return f"<h1>404 NOT FOUND</h>"

    if section not in ['a','b','c','d']:
        return f"<h1>404 NOT FOUND</h>"

    teacher = current_user.teacher[0]
    flag = True
    for course in teacher.courses:
        if course.subject==values[0] and course.year==int(values[1]) and course.branch==values[2].lower() and course.section==values[3].lower():
            temp_course = course
            flag = False
    if flag:
        return redirect("/")

    students_list = []
    student_names = {}
    rows = db.session.query(User).count()
    for i in range(1,rows+1):
        user = User.query.get(i)
        if user!=None:
            student = user.student
            if len(student)!=0:
                student = student[0]
                student_names[student.id] = user.first_name
                if student.branch==branch and student.section==section and student.year==year:
                    students_list.append(student)
    print(students_list)
    if request.method=='POST':
        #date = request.form.get("date")
        for student in students_list:
            present_status = request.form.get(str(student.id))
            print(present_status)
            if present_status!=None:
                attendance = Attendance(present_status=True,course_id=temp_course.id,student_id=student.id)
            else:
                attendance = Attendance(present_status=False,course_id=temp_course.id,student_id=student.id)
            db.session.add(attendance)
            db.session.commit()


    return render_template("attendance.html",user=current_user,students_list=students_list,course_name=course_name,student_names=student_names,date=date.today())


@views.route('/attendance')
@login_required
@require_role('s')
def attendance():
    student = current_user.student[0]
    rows = db.session.query(Course).count()
    courses_list = []
    for i in range(1,rows+1):
        course = Course.query.get(i)
        if course!=None:
            student_ids = course.student_ids
            for j in student_ids:
                if j.student_id==student.id:
                    courses_list.append(course)
    attendance_percentages = {}
    for course in courses_list:
        count = 0
        present = 0
        for day in course.attendance:
            if day.student_id==student.id:
                count+=1
                if day.present_status:
                    present+=1
        if count==0:
            attendance_percentages[course.subject]=0
        else:
            attendance_percentages[course.subject]=int((present/count)*100)
    print(attendance_percentages)
    return render_template("progress.html",user=current_user,attendance_percentages=attendance_percentages)


@views.route('/delete-note', methods=['POST'])
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
