from flask import Flask
from .views import vlist_bp
from .models import db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vlist.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # подключаем БД
    db.init_app(app)

    # создаём таблицы (если их ещё нет)
    with app.app_context():
        db.create_all()

    # подключаем blueprint
    app.register_blueprint(vlist_bp, url_prefix='/')

    return app

# это объект, который импортируем в main.py
app = create_app()
