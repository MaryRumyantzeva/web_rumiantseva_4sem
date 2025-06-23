from flask import Flask, redirect, url_for
from .config import Config
from .extensions import db, login_manager, migrate
from flask_wtf import CSRFProtect


csrf = CSRFProtect()

def create_app():
    """Фабрика приложения"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Регистрация blueprints
    from .routes.auth import bp as auth_bp
    from .routes.events import bp as events_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp, url_prefix='/events')


    @app.route('/')
    def exam_home():
        return redirect(url_for('events.index'))
    
    # CLI команды
    from .cli import init_app
    init_app(app)

    csrf.init_app(app)
    
    return app

# Создаем экземпляр приложения для импорта
app = create_app()