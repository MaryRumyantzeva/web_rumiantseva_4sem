from flask_sqlalchemy import SQLAlchemy, event
from flask_login import LoginManager
from flask_migrate import Migrate 
from sqlalchemy.engine import Engine
import sqlite3

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'kp.login'
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    from .models import User  # Импортируем здесь, чтобы избежать циклических импортов
    return User.query.get(int(user_id))

@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):  # только для sqlite
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()