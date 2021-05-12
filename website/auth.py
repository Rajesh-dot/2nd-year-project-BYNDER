from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Student, Teacher
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_required, login_user, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in succesfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")
    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        firstName = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user_type = request.form.get("type")

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email already exists.", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 charecters.", category='error')
        elif len(firstName) < 2:
            flash("First Name must be greater than 1 charecters.", category='error')
        elif password1 != password2:
            flash("Passwords don't match.", category='error')
        elif len(password1) < 7:
            flash("Password must be greater than 6 charecters.", category='error')
        else:
            if user_type.lower() == 's':
                new_user = User(email=email, first_name=firstName, password=generate_password_hash(
                    password1, method='sha256'), user_type=user_type)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash("Account Created!", category='success')
                flash("Please fill the remaining details!", category='success')
                return redirect(url_for('views.student_info'))
            else:
                # add user to data base
                new_user = User(email=email, first_name=firstName, password=generate_password_hash(
                    password1, method='sha256'), user_type=user_type)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                teacher = Teacher(user_id=current_user.id)
                db.session.add(teacher)
                db.session.commit()
                flash("Account Created!", category='success')
                return redirect(url_for('views.add_course'))

    return render_template("sign_up.html", user=current_user)
