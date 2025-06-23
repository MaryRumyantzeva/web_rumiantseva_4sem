from functools import wraps
from flask import Blueprint, request, render_template, url_for, flash, redirect
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..forms import LoginForm,RegistrationForm  
from ..models import User, Role
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
    return User.query.options(db.joinedload(User.role)).get(int(user_id))  # Теперь использует SQLAlchemy-модель




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

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('events.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        contact_info = form.contact_info.data

        # Проверим, есть ли пользователь
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует.', 'warning')
            return redirect(url_for('auth.register'))

        # Назначим роль "user" по умолчанию
        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            flash('Роль "user" не найдена в базе данных.', 'danger')
            return redirect(url_for('auth.register'))

        # Создание пользователя
        user = User(
        username=username,
        password_hash=generate_password_hash(password),
        contact_info=contact_info,
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        middle_name=form.middle_name.data,
        role=user_role
    )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)