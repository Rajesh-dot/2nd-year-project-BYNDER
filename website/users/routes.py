from flask import Blueprint, render_template, request, flash, redirect, url_for
from wtforms.validators import Email
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash
from website import db
from flask_login import login_required, login_user, logout_user, current_user
from .forms import LoginForm, Change_password, UpdateAccountForm, Profile_pic_Form
from website.main.utils import require_role
from datetime import datetime
from website.courses.utils import get_attendance
from .utils import save_picture

users = Blueprint('users', __name__)


'''
-------------------------
 Authantication Section
------------------------
'''


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                flash("Logged in succesfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")
    return render_template("login.html", user=current_user, form=form)


@ users.route("/logout")
@ login_required
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/forget_password', methods=['POST', 'GET'])
def forget_password():
    pass


'''
---------------------
   Profile Section
---------------------

'''


@users.route('/profile')
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


@users.route('/attendance')
@login_required
@require_role('s')
def attendance():
    attendance_percentages = get_attendance()
    values = attendance_percentages.values()
    total = sum(values)//len(values)
    return render_template("progress.html", user=current_user, attendance_percentages=attendance_percentages, total=total)


@users.route('/settings/upload_profile_image', methods=['GET', 'POST'])
@login_required
def upload_profile_pic():
    form = Profile_pic_Form()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_pic = picture_file
            db.session.commit()
            flash("Image uploaded sucessfully", category='success')
    else:
        flash("Please upload an image", category='error')
    return redirect(url_for('users.settings'))


@users.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = UpdateAccountForm()
    form2 = Change_password()
    form3 = Profile_pic_Form()
    if form.validate_on_submit():

        dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d')
        gender = request.form.get('gender')
        current_user.first_name = form.username.data
        current_user.gender = gender
        current_user.mobile = form.mobile.data
        current_user.dob = dob
        db.session.commit()
    elif request.method == 'GET':
        form.username.data = current_user.first_name
        form.mobile.data = current_user.mobile
    image_file = url_for(
        'static', filename='img/' + current_user.profile_pic)
    return render_template("settings.html", user=current_user, form=form, image_file=image_file, form2=form2, form3=form3)


@users.route('/settings/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = Change_password()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.current_password.data):
            current_user.password = generate_password_hash(
                form.new_password.data, method='sha256')
            db.session.commit()
            flash("Password Changed Sucessfully", category="success")
        else:
            flash("Incorrect password, try again.", category="error")
    return redirect(url_for('users.settings'))
