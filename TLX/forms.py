from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask import Flask, render_template
from flask_login import login_required

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

   
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TimeLogForm(FlaskForm):
    start_time = DateTimeField('Start Time', validators=[DataRequired()])
    end_time = DateTimeField('End Time')
    submit = SubmitField('Log Time')

class RequestChangeForm(FlaskForm):
    query = TextAreaField('Request or Query', validators=[DataRequired()])
    submit = SubmitField('Submit')

class GenerateReportForm(FlaskForm):
    report_type = StringField('Report Type', validators=[DataRequired()])
    submit = SubmitField('Generate')
