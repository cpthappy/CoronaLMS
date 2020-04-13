from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app.models import User, Course, Task, Student, Submission, Feedback
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, CourseForm, TaskForm,AddStudentForm, StudentForm, TaskWorkForm
from collections import Counter
import os
import uuid
import babel

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.template_filter('datetime')
def format_datetime(value, format='medium'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE dd.MM.y"
    return babel.dates.format_datetime(value, format)

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

@app.route('/delete_course/<course_id>')
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
    tasks = Task.query.filter_by(course = course).order_by('due_date')
    submissions = Submission.query.with_entities(Submission.task_id, Submission.student_id).\
        filter(Submission.task_id.in_([x.id for x in tasks])).distinct()

    submission_count = Counter()
    for task_id, student_id in submissions:
        submission_count[task_id] += 1 

    student_count = Student.query.filter_by(course = course).count()

    return render_template('manage_course.html', 
                            title='Kurs verwalten', 
                            course=course, 
                            tasks=tasks, 
                            submissions=submission_count,
                            student_count=student_count)

@app.route('/add_task/<course_id>', methods=['GET', 'POST'])
@login_required
def add_task(course_id):
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()
    form = TaskForm()

    if form.validate_on_submit():
        title = form.title.data
        text = form.text.data
        due_date = form.due_date.data
        max_score = form.max_score.data
        task = Task(title = title, text = text, due_date = due_date, course = course, max_score = max_score)
        db.session.add(task)
        db.session.commit()
        flash('Aufgabe ' + title + ' angelegt.')
        return redirect(url_for('manage_course', course_id=course_id))
    elif request.method == 'GET':
        pass

    return render_template('add_task.html', title='Aufgabe anlegen', form=form, course=course)

@app.route('/delete_task/<course_id>/<task_id>')
@login_required
def delete_task(course_id, task_id):
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()
    task = Task.query.filter_by(id = task_id, course=course).first_or_404()
    title = task.title
    db.session.delete(task)
    db.session.commit()
    flash('Aufgabe ' + title + ' gelöscht.')
    return redirect(url_for('manage_course', course_id=course_id))

@app.route('/close_task/<course_id>/<task_id>')
@login_required
def close_task(course_id, task_id):
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()
    task = Task.query.filter_by(id = task_id, course=course).first_or_404()
    title = task.title
    task.is_done = True
    db.session.commit()
    flash('Aufgabe ' + title + ' als abgeschlossen markiert.')
    return redirect(url_for('manage_course', course_id=course_id))

@app.route('/edit_task/<course_id>/<task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(course_id, task_id):
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()
    task = Task.query.filter_by(id=task_id, course=course).first_or_404()
    form = TaskForm()

    if form.validate_on_submit():
        task.title = form.title.data
        task.text = form.text.data
        task.due_date = form.due_date.data
        task.max_score = form.max_score.data
        db.session.commit()
        flash('Aufgabe ' + task.title + ' erfolgreich geändert.')
        return redirect(url_for('manage_course', course_id=course_id))
    elif request.method == 'GET':
        form.title.data = task.title
        form.text.data = task.text
        form.due_date.data = task.due_date 

    return render_template('add_task.html', title='Aufgabe anlegen', form=form, course=course)


def add_students(number, course):
    aliases = [s.alias for s in Student.query.all()]
    names = [s.name for s in Student.query.all()]
    counter = 0
    for i in range(number):
        alias = ''
        name = ''

        while alias == '' or alias in aliases:
            alias = str(uuid.uuid4())[:8]
        aliases.append(alias)
        while name == '' or name in names:
            counter += 1
            name = "Teilnehmer_%0d" % (counter)
        names.append(name)

        student = Student(alias = alias, course= course, name = name)
        db.session.add(student)
    db.session.commit()

@app.route('/students/<course_id>', methods=['GET', 'POST'])
@login_required
def students(course_id):
    form = AddStudentForm()
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()
    students = Student.query.filter_by(course = course)

    if form.validate_on_submit():
        add_students(form.number.data, course)
        flash(str(form.number.data) + ' neue Teilnehmer angelegt.')
    return render_template('students.html', title='Teilnehmer verwalten', form=form, course=course, students=students)

@app.route('/delete_student/<course_id>/<student_id>')
@login_required
def delete_student(course_id, student_id):
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()
    student = Student.query.filter_by(id = student_id, course=course).first_or_404()
    db.session.delete(student)
    db.session.commit()
    flash('Teilnehmer  gelöscht.')
    return redirect(url_for('students', course_id=course_id))

@app.route('/work/<student_alias>', methods=['GET', 'POST'])
def work(student_alias):
    form = StudentForm()
    student = Student.query.filter_by(alias= student_alias).first_or_404()
    course = Course.query.filter_by(id = student.course_id).first_or_404()
    tasks = Task.query.filter_by(course = course).order_by("due_date")
    student.last_seen = datetime.utcnow()
    db.session.commit()

    if form.validate_on_submit():
        student.email = form.email.data
        student.name = form.name.data
        db.session.commit()
    else:
        form.email.data = student.email
        form.name.data = student.name

    return render_template('view_course_student.html', course=course, tasks=tasks, student = student, form=form)

@app.route('/task/<student_alias>/<task_id>', methods=['GET', 'POST'])
def task(student_alias, task_id):
    form = TaskWorkForm()
    student = Student.query.filter_by(alias= student_alias).first_or_404()
    task = Task.query.filter_by(id=task_id).first_or_404()
    submissions = Submission.query.filter_by(task_id=task.id, student_id=student.id)
    student.last_seen = datetime.utcnow()
    db.session.commit()

    if form.validate_on_submit() and not task.is_done:
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            filename, file_extension = os.path.splitext(original_filename)
            filename = str(uuid.uuid4())
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + "." + file_extension))
            submission = Submission(student_id = student.id, task_id =task.id, filename=filename+"."+file_extension, original_name=original_filename)
            db.session.add(submission)
            db.session.commit()
            flash(original_filename + ' gespeichert.')
    else:
        pass
    return render_template('view_task_student.html', task=task, student = student, submissions=submissions, form=form)

@app.route('/delete_submission/<student_alias>/<submission_id>/<task_id>')
def delete_submission(student_alias, submission_id, task_id):
    student = Student.query.filter_by(alias = student_alias).first_or_404()
    submission = Submission.query.filter_by(id = submission_id, student_id=student.id).first_or_404()
    name = submission.original_name
    path = os.path.join(app.config['UPLOAD_FOLDER'], submission.filename)
    os.remove(path)
    db.session.delete(submission)
    db.session.commit()
    flash('Datei ' + name + ' gelöscht.')
    return redirect(url_for('task', student_alias = student_alias, task_id = task_id))

@app.route('/missing/<course_id>/<task_id>')
@login_required
def missing_submissions(course_id, task_id):
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()
    task = Task.query.filter_by(id = task_id).first_or_404()
    submissions = Submission.query.filter_by(task_id = task.id).with_entities(Submission.student_id)
    missing_students = Student.query.filter(~Student.id.in_(submissions))
    return render_template('missing_submissions.html', task=task, course = course, missing_students=missing_students)

@app.route('/feedback/<course_id>/<task_id>')
@login_required
def feedback_submissions(course_id, task_id):
    course = Course.query.filter_by(id = course_id, author = current_user).first_or_404()
    task = Task.query.filter_by(id = task_id).first_or_404()
    submissions = Submission.query.filter_by(task_id = task.id).with_entities(Submission.student_id).distinct()
    submissions = Student.query.filter(Student.id.in_(submissions))
    return render_template('feedback_submissions.html', task=task, course = course, submissions=submissions)