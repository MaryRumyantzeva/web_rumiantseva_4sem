from functools import wraps
from flask import Blueprint, request, render_template, url_for, flash, redirect
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..forms import LoginForm
from ..models import User
from ..repositories.user_repository import UserRepository
from ..extensions import db



user_repository = UserRepository(db)

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../../templates/auth')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Требуется авторизация для доступа к этому ресурсу.'
login_manager.login_message_category = 'warning'

from ..models import User  # Уже наследует UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Теперь использует SQLAlchemy-модель




@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('events.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('events.index'))
        flash('Неверные учетные данные', 'danger')
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('events.index'))