from flask import Flask,render_template,redirect,url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, DateTime, ForeignKey,Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from forms import AddTaskForm,EditTaskForm,RegisterForm
from datetime import datetime,date
import calendar

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
    add_date:Mapped[datetime] = mapped_column(DateTime,nullable=False)
    task:Mapped[str] = mapped_column(String,nullable=False)
    complete:Mapped[bool] = mapped_column(Boolean,default=False)
    complete_date: Mapped[datetime] = mapped_column(DateTime,nullable=True)
    
    #relationship
    # user_task_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    # user_task: Mapped['User'] = relationship(back_populates='tasks')

with app.app_context():
    db.create_all()

now = datetime.now()

@app.context_processor
def inject_date():
    return {
        'current_year': now.year,
        'current_month': now.month,
        'current_day': now.day,
        'current_time': now.second,
    }

@app.route('/')
def home():
    tasks = []
    form = AddTaskForm()
    task_info = db.session.execute(db.select(Task).order_by(Task.add_date.desc())).scalars().all()

    for item in task_info:
        tasks.append(item)
    return render_template('index.html',form=form,task_info_forms=tasks)


@app.route('/add',methods=['POST','GET'])
def add_task():
    form = AddTaskForm()
    if form.validate_on_submit():
        new_task = Task(
            task = form.task.data,
            add_date = form.task_date.data,
        )
        db.session.add(new_task)
        db.session.commit()

    return redirect(url_for('home'))


@app.route('/complete/<int:id>',methods=['POST','GET'])
def complete_task(id):
    task = db.get_or_404(Task,id)
    #最初にFalseをデフォルトにつけているので not Falseで Trueにしている。
    task.complete = not task.complete

    #タスクが完了しているものを再度押した時、データベースにある日付をからにする
    if task.complete:
        #終了した日付と時間を書いている。
        task.complete_date = datetime.now()
    else:
        task.complete_date = None

    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete/<int:id>',methods=['POST','GET'])
def delete_task(id):
    todo_info = db.get_or_404(Task,id)

    delete_form = EditTaskForm(
        task = todo_info.task,
        task_date = todo_info.add_date,
        complete = todo_info.complete,
    )
    delete_form.submit.label.text = "Delete"

    if delete_form.validate_on_submit():
        db.session.delete(todo_info)
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template('edit.html',form=delete_form,is_delete=True)

@app.route('/edit/<int:id>',methods=['POST','GET'])
def edit_task(id):
    todo_info = db.get_or_404(Task,id)

    #edit画面に現在の値、文字を表示させている
    edit_form = EditTaskForm(
        task = todo_info.task,
        task_date = todo_info.add_date,
        complete = todo_info.complete,
    )

    edit_form.submit.label.text = "Edit"


    if edit_form.validate_on_submit():
        todo_info.task = edit_form.task.data
        todo_info.date = edit_form.task_date.data
        todo_info.complete = edit_form.complete.data == 'True'
        db.session.commit()
        return redirect(url_for('home'))
    
    #エラー表示をして原因を探る。一時的に書く
    else:
        print(edit_form.errors)

    return render_template('edit.html',form=edit_form,is_edit=True)


#その月の日付が入ったリストを作成する。typeはdatetime
def make_day_list(year,month):
    day = calendar.monthrange(year,month)
    return [date(year,month,day)for day in range(1,day + 1)]

@app.route('/chart',methods=['POST','GET'])
def charts():
    #やること
    #同じ日付を確認する。何個あるか確認する

    
    labels = [d.strftime("%m/%d") for d in make_day_list(2026,7)]
    return render_template('chart.html')




if __name__ == '__main__':
    app.run(debug=True)
