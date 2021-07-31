from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..models import Note, Student, Teacher, Array_ids
from website import db
from website.main.utils import require_role
import json
from .forms import NoticeForm, EditPostForm

notices = Blueprint('notices', __name__)


@ notices.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})


@notices.route('/addpost', methods=['GET', 'POST'])
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


@notices.route('/my_notices', methods=['GET', 'POST'])
@login_required
@require_role(role="p")
def my_notices():
    notes = current_user.notes
    return render_template('my_notices.html',user=current_user,notes=notes)


@notices.route('/notice/<id>', methods=['GET', 'POST'])
@login_required
@require_role(role="p")
def notice_view(id):
    note = Note.query.get(id)
    if note and note.author.id:
        form = EditPostForm()
        if request.method == 'GET':
            form.title.data = note.title
            form.content.data = note.data
        if form.validate_on_submit():
            note.title = form.title.data
            note.data = form.content.data
            db.session.commit()
            flash('Posted edited sucessfully', category='success')
            return redirect(url_for('notices.my_notices'))
        return render_template("edit_notice.html",user=current_user,note=note,form=form)
    else:
        return f"<h1>404 page not found</h1>"


@notices.route('/notice/<id>/delete', methods=['GET', 'POST'])
@login_required
@require_role(role="p")
def delete_post(id):
    note = Note.query.get(id)
    if note and note.author.id:
        db.session.delete(note)
        db.session.commit()
        flash('Post deleted successfully', category='success')
        return redirect('/')
    else:
        return f"<h1>404</h1>"

