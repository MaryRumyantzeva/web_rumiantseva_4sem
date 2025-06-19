import os
from kp import create_app
from kp.extensions import db

def reset_database():
    app = create_app()
    
    with app.app_context():
        # Принудительно удаляем и создаем таблицы
        db.drop_all()
        db.create_all()
        
        # Проверка
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        print("Созданные таблицы:", inspector.get_table_names())
        
        # Создаем тестовых пользователей
        from kp.models import User
        if not User.query.first():
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('admin123')
            
            user = User(username='user', email='user@example.com')
            user.set_password('user123')
            
            db.session.add(admin)
            db.session.add(user)
            db.session.commit()
            print("Тестовые пользователи созданы")

if __name__ == '__main__':
    reset_database()