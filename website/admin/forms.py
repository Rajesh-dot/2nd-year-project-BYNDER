from ..models import User
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.fields.core import SelectField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DecimalField, TextAreaField
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm


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


class AddCourse(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    teacher_id = StringField('Teacher_id', validators=[DataRequired()])
    submit = SubmitField('Post')
