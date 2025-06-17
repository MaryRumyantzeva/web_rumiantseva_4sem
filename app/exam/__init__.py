from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    
    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Регистрация blueprints
    from .routes.auth import bp as auth_bp
    from .routes.events import bp as events_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    
    # Инициализация CLI команд
    from .cli import init_app
    init_app(app)
    
    return app

app = create_app()