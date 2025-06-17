import os
from flask import Flask
from .extensions import init_extensions, photos
from .config import Config
from flask_wtf.csrf import CSRFProtect
from flask_uploads import UploadSet, IMAGES, configure_uploads

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
    
    # Настройка загрузки файлов
    photos = UploadSet('photos', IMAGES)  # Теперь IMAGES доступен
    app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        'static', 'uploads'
    )
    configure_uploads(app, photos)
    
    # Инициализация расширений (DB, LoginManager, Migrate)
    init_extensions(app)
    
    # Регистрация Blueprints
    register_blueprints(app)

    from .extensions import init_uploads
    init_uploads(app)

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

# Добавляем обработчик для сервирования загруженных файлов
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

if __name__ == '__main__':
    import os
    # Создаём папку для загрузок, если её нет
    os.makedirs(app.config['UPLOADED_PHOTOS_DEST'], exist_ok=True)
    app.run()