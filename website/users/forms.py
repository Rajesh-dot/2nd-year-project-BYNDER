from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DecimalField, TextAreaField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=30)])
    mobile = DecimalField('Mobile', validators=[DataRequired()])
    submit = SubmitField('Update')


class Change_password(FlaskForm):
    current_password = PasswordField('current password', validators=[
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


class Profile_pic_Form(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('upload')
