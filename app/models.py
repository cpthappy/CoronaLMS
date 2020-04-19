from datetime import datetime
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from app import login
from sqlalchemy.dialects.postgresql import UUID
import uuid


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    courses = db.relationship('Course', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    institution = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    show_email = db.Column(db.Boolean, unique=False, default=False)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)    

def generate_link():
    return uuid.uuid4().hex


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    link = db.Column(db.String(32), default=generate_link, nullable=True)
    tasks = db.relationship('Task', backref='course', lazy='dynamic')
    students = db.relationship('Student', backref='course', lazy='dynamic')

    def __repr__(self):
        return '<Course {}>'.format(self.title)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    text = db.Column(db.String(21000))
    due_date = db.Column(db.DateTime)
    max_score = db.Column(db.Integer, nullable=True)
    is_done = db.Column(db.Boolean, default=False)
    is_visible = db.Column(db.Boolean, default=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    submissions = db.relationship('Submission', backref='task', lazy='dynamic')
    scores = db.relationship('Feedback', backref='task', lazy='dynamic')
    messages = db.relationship('Message', backref='task', lazy='dynamic')

    def __repr__(self):
        return '<Task {}>'.format(self.title)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    alias = db.Column(db.String(32))
    email = db.Column(db.String(64), nullable=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    submissions = db.relationship('Submission', backref='student', lazy='dynamic')
    scores = db.relationship('Feedback', backref='student', lazy='dynamic')

    def __repr__(self):
        return '<Student {}>'.format(self.title)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256))
    original_name = db.Column(db.String(256))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    text = db.Column(db.String)
    score = db.Column(db.Integer)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2048), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    student_alias = db.Column(db.String(32), nullable=True)
    user_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(64), nullable=True)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))