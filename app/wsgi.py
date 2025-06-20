import sys
import os

# Абсолютный путь до папки, где лежит твоя app.py
project_home = '/home/rumiantseva/web_rumiantseva_4sem'

# Добавляем в sys.path, если не добавлено
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Теперь можно импортировать
from app.app import app  # путь до DispatcherMiddleware объекта

# Если запускается как main — не нужно, PythonAnywhere сам запустит
