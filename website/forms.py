from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DecimalField, TextAreaField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png', 'jpeg'])])
    mobile = DecimalField('Mobile', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'That email is taken. Please choose a different one.')


class AddStudent(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    regno = StringField('Regno', validators=[DataRequired()])
    mobile = DecimalField('Mobile', validators=[DataRequired()])
    submit = SubmitField('Add_Student')


class AddTeacher(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    teacher_id = StringField('Teacher_Id', validators=[DataRequired()])
    mobile = DecimalField('Mobile', validators=[DataRequired()])
    submit = SubmitField('Add_Teacher')


class NoticeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class AddCourse(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    teacher_id = StringField('Teacher_id', validators=[DataRequired()])
    submit = SubmitField('Post')


class Change_password(FlaskForm):
    password = PasswordField('password', validators=[
                             DataRequired(), Length(min=4, max=30)])
    new_password = PasswordField('new_Password', validators=[
                                 DataRequired(), Length(min=4, max=30)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('new_password'), Length(min=4, max=30)])
    submit = SubmitField('Update')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                'There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
