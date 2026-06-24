from flask import Flask,render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from forms import listform
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

class List(db.Model):
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    date:Mapped[datetime] = mapped_column(DateTime,nullable=False)
    task:Mapped[str] = mapped_column(String,nullable=False)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    form = listform()
    return render_template('index.html',form=form)


@app.route('/add')
def add_task():
    pass

if __name__ == '__main__':
    app.run(debug=True)
