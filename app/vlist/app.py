import os
from flask import Flask
from flask_migrate import Migrate
from .views import vlist_bp
from .models import db

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vlist.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path,  "static", "uploads")

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # подключаем БД
    db.init_app(app)
    migrate = Migrate(app, db)

    # создаём таблицы (если их ещё нет)
    with app.app_context():
        db.create_all()

    # подключаем blueprint
    app.register_blueprint(vlist_bp, url_prefix='/')

    return app


# это объект, который импортируем в main.py
app = create_app()
