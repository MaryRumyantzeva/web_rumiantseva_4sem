import sys
import os

# путь к корневой папке проекта, на один уровень выше app/
project_path = '/home/rumiantseva/web_rumiantseva_4sem'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# иногда нужно явно указать путь к папке с app
os.chdir(project_path)


# Теперь можно импортировать
from app.app import app  # путь до DispatcherMiddleware объекта

# Если запускается как main — не нужно, PythonAnywhere сам запустит
