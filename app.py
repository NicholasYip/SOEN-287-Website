# Nicholas Yiphoiyen, 40117237
# SOEN287, assignment 2, section W, Winter 2020

from datetime import date
from flask import Flask, render_template, url_for, redirect, session, flash
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from forms import *

app = Flask(__name__)
app.secret_key = 'kazukigonzalezadachi'
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['USE_SESSION_FOR_NEXT'] = True

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = '40117237nicholas@gmail.com'
app.config['MAIL_PASSWORD'] = '40117237Nicholas1!'
mail = Mail(app)


class User(UserMixin):
    def __init__(self, fname, lname, username, password, email):
        self.fname = fname
        self.lname = lname
        self.id = username
        self.password = password
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    user = find_user(user_id)
    if user:
        user.password = None
    return user


def classify():
    today = str(date.today())
    f = open('data/notes.csv', 'r')
    g = open('data/valid.csv', 'w', newline='')
    h = open('data/expired.csv', 'w', newline='')
    for row in csv.reader(f):
        if len(row) != 5:
            continue
        elif row[2] >= today:
            writer = csv.writer(g)
            writer.writerow(row)
        else:
            writer = csv.writer(h)
            writer.writerow(row)
    g.close()
    h.close()


def receiver():
    newsletter = Newsletter()
    if newsletter.validate_on_submit():
        msg = Message('Welcome to the newsletter!', sender='40117237nicholas@gmail.com', recipients=[newsletter.newsletter.data])
        msg.body = '''Thanks for subscribing to my newsletter. Look forward to receiving my cool future inventions!!'''
        mail.send(msg)
    return newsletter


def find_user(username):
    with open('data/accounts.csv', encoding="utf-8-sig") as f:
        for line in f:
            lines = line.split(',')
            if len(lines) != 5:
                continue
            if username == lines[2]:
                lines[4] = line[4].strip('\n')
                return User(lines[0], lines[1], lines[2], lines[3], lines[4])
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    newsletter = receiver()
    form = LoginForm()
    if form.validate_on_submit():
        user = find_user(form.username.data)
        if user and check_password_hash(user.password, form.password.data):
            flash('Logged in successfully.')
            login_user(user)
            next_page = session.get('next', '/')
            session['next'] = '/'
            return redirect(next_page)
        else:
            flash('Incorrect username/password!')
    return render_template('login.html', form=form, newsletter=newsletter)


@app.route('/', methods=['GET', 'POST'])
def home():
    newsletter = receiver()
    return render_template('Home.html', username=session.get('username'), newsletter=newsletter)


@app.route('/creation', methods=['GET', 'POST'])
@login_required
def creation():
    newsletter = receiver()
    form = Note()
    if form.validate_on_submit():
        with open('data/notes.csv', 'a', encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([form.title.data, form.color.data, form.date.data, form.text.data, current_user.fname])
        return redirect(url_for('creatednote', title=form.title.data))
    return render_template('creationnote.html', form=form, newsletter=newsletter)


@app.route('/creatednote/<title>', methods=['GET', 'POST'])
@login_required
def creatednote(title):
    classify()
    newsletter = receiver()
    return render_template('creatednote.html', title=title, newsletter=newsletter)


@app.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar():
    classify()
    newsletter = receiver()
    return render_template('Calendar.html', newsletter=newsletter)


@app.route('/trashcan', methods=['GET', 'POST'])
@login_required
def trashcan():
    newsletter = receiver()
    classify()
    expired = []
    with open('data/expired.csv', encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if len(row) != 5:
                continue
            else:
                expired.append(row)
    return render_template('Trashcan.html', newsletter=newsletter, expired=expired)


@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    newsletter = receiver()
    classify()
    form = Report()
    if form.validate_on_submit():
        with open('data/report.csv', 'a', encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([form.title.data, form.message.data, current_user.fname])
        with open('data/notes.csv','r', encoding="utf-8-sig") as g:
            for row in csv.reader(g):
                if len(row) != 5:
                    continue
                if row[0] == form.title.data:
                    exist = True
                    break
                else:
                    exist = False
        if exist:
            return redirect(url_for('reportsent', title=form.title.data))
        else:
            return redirect(url_for('badreport', title=form.title.data))
    return render_template('report.html', newsletter=newsletter, form=form)

@app.route('/badreport/<title>', methods=['GET', 'POST'])
@login_required
def badreport(title):
    newsletter = receiver()
    classify()
    return render_template('badreport.html', newsletter=newsletter, title=title)

@app.route('/reportsent/<title>', methods=['GET', 'POST'])
@login_required
def reportsent(title):
    newsletter = receiver()
    classify()
    return render_template('reportafter.html', newsletter=newsletter, title=title)


@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    newsletter = receiver()
    classify()
    form = Comment()
    if form.validate_on_submit():
        with open('data/comment.csv', 'a', encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([form.message.data, current_user.fname])
        return (redirect(url_for('comment', user = current_user.fname)))
    return render_template('contact.html', newsletter=newsletter, form=form)


@app.route('/comment/<user>', methods=['GET', 'POST'])
@login_required
def comment(user):
    newsletter = receiver()
    classify()
    return render_template('commentafter.html', newsletter=newsletter, user=user)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = Search()
    newsletter = receiver()
    classify()
    if form.validate_on_submit():
        return redirect(url_for('searchresults', word=form.word.data))
    return render_template('Search.html', form=form, newsletter=newsletter)


@app.route('/search/<word>', methods=['GET', 'POST'])
@login_required
def searchresults(word):
    newsletter = receiver()
    wordnotes = []
    with open('data/valid.csv', encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if len(row) != 5:
                continue
            if any(word in item for item in row):
                wordnotes.append(row)
    return render_template('searchresults.html', newsletter=newsletter, word=word, wordnotes=wordnotes)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    newsletter = receiver()
    form = SignUp()
    if form.validate_on_submit():
        user = find_user(form.username.data)
        if not user:
            password = generate_password_hash(form.password.data, method='sha256')
            with open('data/accounts.csv', 'a', encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow([form.fname.data, form.lname.data, form.username.data, password, form.email.data])
            flash('Registered successfully.')
            return redirect(url_for('createdacc', fname=form.fname.data))
        else:
            flash('This username already exists, choose another one')
    return render_template('signup.html', form=form, newsletter=newsletter)


@app.route('/createdacc/<fname>', methods=['GET', 'POST'])
def createdacc(fname):
    newsletter = receiver()
    return render_template('createdacc.html', fname=fname, newsletter=newsletter)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/note/<date>', methods=['GET', 'POST'])
@login_required
def today(date):
    newsletter = receiver()
    daynotes = []
    with open('data/valid.csv', encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if len(row) != 5:
                continue
            if str(row[2]) == str(date):
                daynotes.append(row[0])
    print(daynotes)
    return render_template('datenotes.html', notes=daynotes, date=date, newsletter=newsletter)


if __name__ == '__main__':
    app.debut = True
    app.run()
