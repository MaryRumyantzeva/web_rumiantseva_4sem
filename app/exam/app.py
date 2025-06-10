from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Event, VolunteerRegistration, Role
from forms import LoginForm, EventForm, RegistrationForm
from werkzeug.utils import secure_filename
import os
import markdown
import bleach

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Конфигурация загрузки файлов
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    events = Event.query.filter(Event.date >= datetime.now()).order_by(Event.date.desc()).paginate(page=page, per_page=10)
    return render_template('index.html', events=events)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
        flash('Невозможно аутентифицироваться с указанными логином и паролем')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/event/<int:event_id>')
def event(event_id):
    event = Event.query.get_or_404(event_id)
    description_html = markdown.markdown(event.description)
    # Очистка HTML от потенциально опасных тегов
    description_html = bleach.clean(description_html)
    return render_template('event.html', event=event, description=description_html)

# Другие маршруты для добавления/редактирования мероприятий, регистрации волонтеров и т.д.

if __name__ == '__main__':
    app.run(debug=True)