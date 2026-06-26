from flask_wtf import FlaskForm
from wtforms import StringField,DateField,SubmitField
from wtforms.validators import DataRequired

class TaskForm(FlaskForm):
    task = StringField('New Task', validators=[DataRequired()])
    task_date = DateField(format='%Y-%m-%d',validators=[DataRequired()])
    submit = SubmitField('Add')

class RegisterForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired()])
    password = StringField('Password',validators=[DataRequired()])
    submit = SubmitField('Sign up')