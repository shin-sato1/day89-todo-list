from flask_wtf import FlaskForm
from wtforms import StringField,DateField,SubmitField
from wtforms.validators import DataRequired

class listform(FlaskForm):
    task = StringField('New Task', validators=[DataRequired()])
    task_date = DateField(format='%Y-%m-%d',validators=[DataRequired()])
    submit = SubmitField('Add')