from flask import Flask,render_template,redirect,url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, DateTime, ForeignKey,Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from forms import TaskForm
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
bootstrap = Bootstrap5(app)

# create database
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
db.init_app(app)

# class User(db.Model):
#     id:Mapped[int] = mapped_column(Integer,primary_key=True)
#     name: Mapped[str] = mapped_column(String,nullable=False)
#     email: Mapped[str] = mapped_column(String,unique=True,nullable=False)
#     password: Mapped[str] = mapped_column(String,nullable=False)
#     #relationship
#     tasks: Mapped[list['Task']] = relationship(back_populates='user_task')

class Task(db.Model):
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    date:Mapped[datetime] = mapped_column(DateTime,nullable=False)
    task:Mapped[str] = mapped_column(String,nullable=False)
    complete:Mapped[bool] = mapped_column(Boolean,default=False)
    #relationship
    # user_task_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    # user_task: Mapped['User'] = relationship(back_populates='tasks')

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    tasks = []
    form = TaskForm()
    task_info = db.session.execute(db.select(Task).order_by(Task.date.desc())).scalars().all()

    for item in task_info:
        tasks.append(item)
    return render_template('index.html',form=form,task_info_forms=tasks)


@app.route('/add',methods=['POST','GET'])
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(
            task = form.task.data,
            date = form.task_date.data,
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/complete/<int:id>',methods=['POST'])
def complete_task(id):
    task = db.get_or_404(Task,id)
    task.complete = not task.complete

    db.session.commit()
    return redirect(url_for('home'))
    

if __name__ == '__main__':
    app.run(debug=True)
