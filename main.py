import os
from dotenv import load_dotenv
from flask import Flask,render_template,redirect,url_for,request,flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, DateTime, ForeignKey,Boolean,func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from forms import AddTaskForm,EditTaskForm,RegisterForm,LoginForm
from datetime import datetime,date
import calendar

load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
bootstrap = Bootstrap5(app)

# create database
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
db.init_app(app)


class User(db.Model,UserMixin):
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String,nullable=False)
    email: Mapped[str] = mapped_column(String,unique=True,nullable=False)
    password: Mapped[str] = mapped_column(String,nullable=False)

    #relationship
    tasks: Mapped[list['Task']] = relationship(back_populates='user_task')

class Task(db.Model):
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    add_date:Mapped[datetime] = mapped_column(DateTime,nullable=False)
    task:Mapped[str] = mapped_column(String,nullable=False)
    complete:Mapped[bool] = mapped_column(Boolean,default=False)
    complete_date: Mapped[datetime] = mapped_column(DateTime,nullable=True)
    
    #relationship
    user_task_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    user_task: Mapped['User'] = relationship(back_populates='tasks')

#create table
with app.app_context():
    db.create_all()


#create login_manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,int(user_id))


#create datetime module for inject_date
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
    # task_info = db.session.execute(db.select(Task).order_by(Task.add_date.desc())).scalars().all()
    
    if current_user.is_authenticated:
        task_info = current_user.tasks
    else:
        task_info = []

    for item in task_info:
        tasks.append(item)
    return render_template('index.html',form=form,task_info_forms=tasks)



@app.route('/add',methods=['POST','GET'])
def add_task():
    form = AddTaskForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please sign up to create todo list","error")
            return redirect(url_for('register'))
        
        new_task = Task(
            task = form.task.data,
            add_date = form.task_date.data,
            user_task_id = current_user.id
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
        todo_info.add_date = edit_form.task_date.data
        todo_info.complete = edit_form.complete.data == 'True'
        db.session.commit()
        return redirect(url_for('home'))
    
    #エラー表示をして原因を探る。一時的に書く
    else:
        print(edit_form.errors)

    return render_template('edit.html',form=edit_form,is_edit=True)



@app.route('/chart',methods=['POST','GET'])
def charts():
    #やること
    #同じ日付を確認する。何個あるか確認する

    year = request.args.get('year')
    month = request.args.get('month')

    if year is None or month is None:
        year = now.year
        month = now.month
    else:
        year = int(year)
        month = int(month)


    chart_label = f'{year}年{month}月'

    #下のコードわからない

    #その月の日付が入ったリストを作成する。typeはdatetime
    last_day = calendar.monthrange(year,month)[1]
    date_list = [
        date(year,month,day)
        for day in range(1,last_day + 1)
    ]

    result = (
        db.session.execute(
            db.select(
                func.date(Task.complete_date),
                func.count(Task.id)
            )
            .where(Task.user_task_id == current_user.id)
            .where(func.strftime("%Y",Task.complete_date) == str(year))
            .where(func.strftime("%m",Task.complete_date) == f"{month:02d}")
            .group_by(func.date(Task.complete_date))
        )
        .all()
    )
    
    #[('2026-07-01', 1)]の形を辞書に変換する
    count_dict = {
        day: count
        for day,count in result
    }
    
    labels = []
    data = []
    for d in date_list:
        labels.append(f"{d.day}")
        data.append(count_dict.get(str(d),0))

    return render_template('chart.html',labels=labels,data=data,chart_label=chart_label)


@app.route('/register',methods=['POST','GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        already_user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if already_user:
                flash("You've already sign up with that email,log in instead","error")
                return redirect(url_for('login'))
        
        hashed_password = generate_password_hash(
            password=password,
            method='pbkdf2:sha256',
            salt_length=8,
        )

        new_user = User(
            name = name,
            email = email,
            password = hashed_password,
        )

        db.session.add(new_user)
        db.session.commit()

        #login for new user
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html',form=form)

#ログインした後
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        check_login_user = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalar()

        if not check_login_user:
            flash(message='That email does not exsit, Please try again',category='error')
            return redirect(url_for('login'))

        else:
            check_password = check_password_hash(
                pwhash = check_login_user.password,
                password = password
            )
            if not check_password:
                flash(message='Password incorrect, Please try again',category='error')
                return redirect(url_for('login'))
            
            else:
                login_user(check_login_user)
                return redirect(url_for('home'))
    return render_template('login.html',form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host="0.0.0.0",port=5001,debug=True)
