from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Course, Task
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, CourseForm, TaskForm

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    courses = Course.query.filter_by(author = current_user)
    return render_template("index.html", title='Startseite', courses=courses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
       
        if user is None or not user.check_password(form.password.data):
            flash('Ungültiger Benutzername oder falsches Passwort')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
        
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Herzlichen Glückwunsch, sie sind jetzt ein registrierter Benutzer!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    courses = Course.query.filter_by(author = user)
    return render_template('user.html', user=user, course=courses)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.institution = form.institution.data
        db.session.commit()
        flash('Ihre Änderungen wurden gespeichert.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.institution.data = current_user.institution
    return render_template('edit_profile.html', title='Profil bearbeiten',
                           form=form)

@app.route('/add_course', methods=['GET', 'POST'])
@login_required
def add_course():
    form = CourseForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        course = Course(title = title, description = description, author = current_user)
        db.session.add(course)
        db.session.commit()
        flash('Kurs ' + title + ' angelegt.')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        pass
    return render_template('course.html', title='Kurs hinzufügen', form=form)

@app.route('/edit_course/<course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    form = CourseForm()
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()

    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        db.session.commit()
        flash('Kurs ' + course.title + ' geändert.')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.title.data = course.title
        form.description.data = course.description
    return render_template('course.html', title='Kurs bearbeiten', form=form, course_id=course_id)

@app.route('/delete_course/<course_id>', methods=['GET', 'POST'])
@login_required
def delete_course(course_id):
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()
    title = course.title
    db.session.delete(course)
    db.session.commit()
    flash('Kurs ' + title + ' gelöscht.')
    return redirect(url_for('index'))

@app.route('/course/<link>')
def view_course(link):
    course = Course.query.filter_by(link = link).first_or_404()
    tasks = Task.query.filter_by(course = course)
    return render_template('view_course.html', course=course, tasks=tasks)

@app.route('/manage_course/<course_id>')
@login_required
def manage_course(course_id):
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()

    return render_template('manage_course.html', title='Kurs verwalten', course=course)

@app.route('/add_task/<course_id>', methods=['GET', 'POST'])
@login_required
def add_task(course_id):
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()
    form = TaskForm()

    if form.validate_on_submit():
        title = form.title.data
        text = form.text.data
        due_date = form.due_date.data
        task = Task(title = title, text = text, course = course)
        db.session.add(task)
        db.session.commit()
        flash('Aufgabe ' + title + ' angelegt.')
        return redirect(url_for('manage_course', course_id=course_id))
    elif request.method == 'GET':
        pass

    return render_template('add_task.html', title='Aufgabe anlegen', form=form, course=course)