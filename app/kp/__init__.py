from flask import Flask, redirect, url_for
from .config import Config
from .extensions import db, login_manager, migrate

def create_app():
    """Фабрика приложения"""
    app = Flask(__name__)
    app.config.from_object(Config)
        
    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Регистрация blueprints
    from .routes import bp as kp_bp  
    app.register_blueprint(kp_bp)


    @app.route('/')
    def exam_home():
        return redirect(url_for('kp_bp.home'))
    
    # CLI команды
    from .cli import init_app
    init_app(app)

    @app.route('/test')
    def test_route():
        return "KP app is working! Blueprint routes: " + str(app.url_map)
    
    return app
    
    return app

# Создаем экземпляр приложения для импорта
app = create_app()