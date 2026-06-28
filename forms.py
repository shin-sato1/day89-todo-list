from flask_wtf import FlaskForm
from wtforms import StringField,DateField,SubmitField,SelectField
from wtforms.validators import DataRequired,InputRequired

class AddTaskForm(FlaskForm):
    task = StringField('Add Task', validators=[DataRequired()])
    task_date = DateField('Execute date',format='%Y-%m-%d',validators=[DataRequired()])
    submit = SubmitField('Add')

class EditTaskForm(FlaskForm):
    task = StringField('Add Task', validators=[DataRequired()])
    task_date = DateField('Execute date',format='%Y-%m-%d',validators=[DataRequired()])
    complete = SelectField('Status',validators=[InputRequired()],choices=[('True','Complete'),('False','Incomplete')])
    submit = SubmitField('Add')

class RegisterForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired()])
    password = StringField('Password',validators=[DataRequired()])
    submit = SubmitField('Sign up')