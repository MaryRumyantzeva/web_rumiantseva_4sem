'''from . import app


if __name__ == '__main__':
    app.run(debug=True)'''
import os
from flask import Flask
from .extensions import init_extensions
from .config import Config  # Импортируем конфиг
from flask_wtf.csrf import CSRFProtect

def create_app():
    # Создание экземпляра Flask
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    
    # Загрузка конфигурации
    app.config.from_object(Config)

    # Инициализация CSRF
    csrf = CSRFProtect(app)
    
    # Инициализация расширений (DB, LoginManager, Migrate)
    init_extensions(app)
    
    # Регистрация Blueprints
    register_blueprints(app)

    @app.context_processor
    def inject_csrf():
        return dict(csrf_token=csrf.generate_csrf)
    
    return app

def register_blueprints(app):
    """Регистрирует все Blueprints приложения"""
    from .routes.auth import bp as auth_bp
    from .routes.events import bp as events_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)

# Создаем экземпляр приложения
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)