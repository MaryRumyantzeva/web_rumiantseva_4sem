import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, AnonymousUserMixin
from flask_migrate import Migrate
from functools import wraps
from flask import flash, redirect, url_for, current_app
from flask_login import current_user


# Инициализация основных расширений
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()



# Создаем класс для пустой пагинации
class EmptyPagination:
    def __init__(self):
        self.page = 1
        self.per_page = 10
        self.total = 0
        self.items = []
        self.pages = 0
        self.has_prev = False
        self.has_next = False
        self.prev_num = None
        self.next_num = None

def create_empty_pagination():
    return EmptyPagination()

@login_manager.user_loader
def load_user(user_id):
    from .models import User  # Отложенный импорт
    return User.query.get(int(user_id))

class AnonymousUser(AnonymousUserMixin):
    """Кастомный класс для анонимных пользователей с mock-ролью"""
    @property
    def role(self):
        # Создаем легковесный объект роли с минимальными атрибутами
        return type('Role', (), {
            'name': 'guest',
            'id': None,
            'description': 'Неавторизованный пользователь',
            'is_admin': False,
            'is_moderator': False
        })()

    @property
    def is_authenticated(self):
        return False

# Конфигурация LoginManager
login_manager.anonymous_user = AnonymousUser
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Требуется авторизация для доступа к этой странице'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    """Кастомный загрузчик пользователя с обработкой исключений"""
    from .models import User  # Отложенный импорт
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        current_app.logger.error(f"Error loading user {user_id}: {str(e)}")
        return None

def role_required(*roles):
    """Улучшенный декоратор для проверки ролей с кешированием"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            
            # Проверяем кешированный атрибут has_role если он есть
            if hasattr(current_user, '_cached_roles'):
                has_access = any(role in current_user._cached_roles for role in roles)
            else:
                has_access = current_user.role.name in roles
            
            if not has_access:
                flash('Доступ запрещен. Недостаточно прав.', 'danger')
                return redirect(url_for('events.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def init_extensions(app):
    """
    Полная инициализация расширений в приложении Flask
    с дополнительными проверками конфигурации
    """
    # Проверка обязательных конфигов
    required_config = [
        'SECRET_KEY',
        'SQLALCHEMY_DATABASE_URI',
        'UPLOAD_FOLDER'
    ]
    
    for config in required_config:
        if config not in app.config:
            raise RuntimeError(f"Missing required config: {config}")
    
    # Инициализация основных расширений
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
   
    
    # Оптимальные настройки для SQLAlchemy
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    app.config.setdefault('SQLALCHEMY_ENGINE_OPTIONS', {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
        'connect_args': {'connect_timeout': 5}
    })
    
    # Создаем папку для загрузок если не существует
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    