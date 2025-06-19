# check_tables.py
from app.kp.app import app
from app.kp.extensions import db

with app.app_context():
    print("Таблицы в БД:", db.engine.table_names())
