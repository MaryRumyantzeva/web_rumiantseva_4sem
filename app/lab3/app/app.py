from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

app = Flask(__name__)

application = app
 
app.config.from_pyfile('config.py')

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'
login_manager.login_message = 'Authentication is required for access'
login_manager.login_message_category = 'warning'


users = [
    {
        'id': 1,
        'login': 'user',
        'password': '123',
    },
]


class User(UserMixin):
    def __init__(self, user_id, user_login):
        self.id = user_id
        self.login = user_login


@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user['id'] == int(user_id):
            return User(user['id'], user['login'])
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/counter')
def counter():
    if 'count' in session:
        session['count'] += 1
    else:
        session['count'] = 1
        
    return render_template('counter.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        remember_me = request.form.get('remember_me') == 'on'

        for user in users:
            if login == user['login'] and password == user['password']:
                login_user(User(user['id'], user['login']), remember=remember_me)
                next_url = request.args.get('next')
                flash('You have successfully logged in', 'success')
                return redirect(next_url or url_for('index'))

        flash('Invalid login credentials. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout', methods = ['GET'])
def logout():   
    logout_user()
    return redirect(url_for('index'))

@app.route('/secret', methods = ['GET'])
@login_required
def secret():
    return render_template('secret.html')
    