from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, TextField, SelectField, FileField, IntegerField
from flask_pagedown.fields import PageDownField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from app.models import User, Course, Task

class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Anmelden')


class RegistrationForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Bitte verwenden Sie einen anderen Benutzernamen.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Bitte verwenden Sie eine andere E-Mail.')

class EditProfileForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    about_me = TextAreaField('Über mich', validators=[Length(min=0, max=140)])
    institution = StringField('Insitution', validators = [Length(min=0, max=140)])
    show_mail = BooleanField('E-Mail im Profil anzeigen')
    submit = SubmitField('Speichern')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class CourseForm(FlaskForm):
    title = TextAreaField('Titel', validators=[DataRequired(), Length(min=1, max=140)])
    description = TextAreaField('Beschreibung', validators=[Length(min=0, max=500)])
    submit = SubmitField('Speichern')

class TaskForm(FlaskForm):
    title = TextAreaField('Titel', validators=[DataRequired(), Length(min=1, max=140)])
    text = TextAreaField('Aufgabentext')
    due_date = DateField('Abgabedatum', validators=[Optional()])
    max_score = TextField('Maximale Punktzahl', validators=[Optional()])
    submit = SubmitField('Speichern')

class AddStudentForm(FlaskForm):
    number = SelectField('Anzahl', choices=[(x,x) for x in range(1,31)], default=1, coerce=int)
    submit = SubmitField('Anlegen')

class StudentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=64)])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Ändern')

class TaskWorkForm(FlaskForm):
    file = FileField('Lösung hochladen')
    submit = SubmitField('Hochladen')

class FeedbackForm(FlaskForm):
    text = TextAreaField('Feedback')
    score = IntegerField('Punktzahl')
    submit = SubmitField('Speichern')

class MessageForm(FlaskForm):
    text = TextAreaField('Lösung hochladen')
    submit_message = SubmitField('Abschicken')
