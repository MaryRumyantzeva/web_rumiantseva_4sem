import os
from flask import Flask
from .models import User  # Точечный импорт, так как файл в той же папке
from .extensions import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

app = create_app()

with app.app_context():
    # Создаем таблицы
    db.create_all()
    
    # Создаем администратора
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Администратор создан! Логин: admin, Пароль: admin123")
    else:
        print("ℹ️ Пользователь admin уже существует")
    
    print("\nСозданные таблицы:", db.engine.table_names())