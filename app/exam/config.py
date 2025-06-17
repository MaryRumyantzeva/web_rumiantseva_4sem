import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Базовые настройки
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'f038a541489b89f81762d12edfdd03835ceea10cfb3cdbdabfbfa0f48b0d4803'
    
    # Настройки БД (SQLite по умолчанию)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки Flask-Login
    LOGIN_MESSAGE = "Пожалуйста, войдите для доступа"
    LOGIN_MESSAGE_CATEGORY = "warning"
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
    # Настройки загрузки файлов
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Создаем папку для загрузок
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)