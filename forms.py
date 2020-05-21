import csv

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import InputRequired, Email, Length, EqualTo, ValidationError
from wtforms_components import ColorField


class Note(FlaskForm):
    title = StringField('',validators=[InputRequired()])
    color = ColorField ('',validators=[InputRequired()])
    date = DateField('',validators=[InputRequired()])
    text = TextAreaField('',validators=[InputRequired()])
    submit = SubmitField('Create')

class SignUp(FlaskForm):
    fname = StringField('', validators=[InputRequired()])
    lname = StringField('', validators=[InputRequired()])
    username = StringField('', validators=[InputRequired(), Length(3, 64)])
    email = EmailField('', validators=[InputRequired(), Email()])
    password = PasswordField('', validators=[InputRequired(),Length(4,15)])
    password2 = PasswordField('', validators=[InputRequired(),EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Login')

    def validate_password(self, field):
        with open('data/common_passwords.txt') as f:
            for line in f.readlines():
                if field.data == line.strip():
                    raise ValidationError('Your password is too common.')

    def validate_username(self,field):
        with open('data/accounts.csv') as g:
            for row in csv.reader(g):
                if len(row) != 5:
                    continue
                if field.data == row[2]:
                    raise ValidationError("Your username is already in use")

    def validate_email(self,field):
        with open('data/accounts.csv') as g:
            for row in csv.reader(g):
                if len(row) != 5:
                    continue
                if field.data == row[4]:
                    raise ValidationError("Your email is already in use")

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    submit = SubmitField('login')

class Newsletter(FlaskForm):
        newsletter = EmailField('', validators=[Email()])

class Search(FlaskForm):
        word = StringField('', validators=[InputRequired()])

class Report(FlaskForm):
    title = StringField('')
    message = TextAreaField('')

class Comment(FlaskForm):
    message = TextAreaField('', validators=[InputRequired()])