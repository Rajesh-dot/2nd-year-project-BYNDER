from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models import Student, Teacher, Group, Group_student_id, Group_Notices
from website import db
from website.main.utils import require_role
from .forms import NoticeForm

groups = Blueprint('groups', __name__)


@groups.route('/groups')
@login_required
@require_role('s')
def get_groups():
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


@groups.route('/create_group', methods=['GET', 'POST'])
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


@groups.route('/my_groups', methods=['GET', 'POST'])
@login_required
@require_role('p')
def my_groups():
    groups = Group.query.all()
    my_groups_list=[]
    teacher = current_user.teacher[0]
    for group in groups:
        if group.teacher_id==teacher.id:
            my_groups_list.append(group)
    return render_template('my_groups.html',user=current_user,groups=my_groups_list)


@groups.route('/groups/<id>/dashboard', methods=['GET', 'POST'])
@login_required
def group_dashboard(id):
    group = Group.query.get(id)
    if group:
        notes = group.notices
        return render_template('group_dashboard.html',user=current_user,notes=notes,group=group)
    else:
        return f"<h1>404 Page not Found</h1>"


@groups.route('/groups/<id>/add_notice', methods=['GET', 'POST'])
@login_required
def group_add_notice(id):
    group = Group.query.get(id)
    if group:
        form = NoticeForm()
        if form.validate_on_submit():
            group_notice = Group_Notices(title=form.title.data,data=form.content.data,author=current_user.first_name,group_id=group.id)
            db.session.add(group_notice)
            db.session.commit()
            flash('Notice added sucessfully', category='success')
            return redirect(url_for('groups.group_dashboard',id=group.id))
        return render_template('add_group_notice.html',user=current_user,form=form,group=group)
    else:
        return f"<h1>404 Page not Found</h1>"

