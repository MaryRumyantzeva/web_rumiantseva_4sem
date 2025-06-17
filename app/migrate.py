import os
import shutil
from exam import app, db
from flask_migrate import Migrate, init, migrate as _migrate, upgrade

def reset_migrations():
    # Полное удаление папки
    if os.path.exists('migrations'):
        try:
            shutil.rmtree('migrations')
            print("✅ Папка migrations полностью удалена")
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            return False
    return True

def init_migrations():
    if not reset_migrations():
        return
    
    # Инициализация
    Migrate(app, db)
    with app.app_context():
        try:
            init()
            _migrate(message="Initial migration")
            upgrade()
            print("✅ Миграции успешно пересозданы")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("Создаем таблицы напрямую через db.create_all()")
            db.create_all()
            print("✅ Таблицы созданы напрямую")

if __name__ == '__main__':
    init_migrations()