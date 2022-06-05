from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class MainMenu (db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(20), unique=True)
    url = db.Column(db.String(20), unique=True)


class MenuAdmin (db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(20), unique=True)
    url = db.Column(db.String(20), unique=True)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(UserAdmin).get(user_id)


'''Функция, принимающая в качестве аргумента декоратор user_loader, будет вызываться с каждым запросом к серверу. 
Она загружает пользователя из идентификатора пользователя в куки сессии. Flask-Login делает загруженного 
пользователя доступным с помощью прокси current_user.
Он ведет себя как глобальная переменная и доступен как в функциях представления, так и в шаблонах. 
В любой момент времени current_user ссылается либо на вошедшего в систему, либо на анонимного пользователя.'''


class UserAdmin (db.Model, UserMixin):  # Класс UserMixin для декоратора user_loader
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post (db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    image = db.Column(db.Text, default=None)
    url = db.Column(db.String(30), nullable=False, unique=True)


class Course (db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    age = db.Column(db.String(20), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    image = db.Column(db.Text(), default=None)
    url = db.Column(db.String(30), nullable=False, unique=True)

    lessons = db.relationship('Lesson', backref='course')


class Lesson (db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    age = db.Column(db.String(20), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    image = db.Column(db.Text(), default=None)
    url = db.Column(db.String(30), nullable=False, unique=True)

    course_id = db.Column(db.Integer(), db.ForeignKey('courses.id'))

    signups = db.relationship('Signup', backref='lesson')


class Teacher (db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    tel = db.Column(db.String(20), nullable=False, unique=True)
    image = db.Column(db.Text(), default=None)
    age = db.Column(db.Integer(), nullable=False)
    text = db.Column(db.Text())
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    signups = db.relationship('Signup', backref='teacher')


class Signup (db.Model):
    __tablename__ = 'signups'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    tel = db.Column(db.String(20), nullable=False)
    name_child = db.Column(db.String(20))
    age_child = db.Column(db.Integer())
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    teacher_id = db.Column(db.Integer(), db.ForeignKey('teachers.id'))
    lesson_id = db.Column(db.Integer(), db.ForeignKey('lessons.id'))


class FeedBack(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    tel = db.Column(db.String(20), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
