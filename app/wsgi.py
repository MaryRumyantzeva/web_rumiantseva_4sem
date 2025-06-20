import sys
import os

# путь к корневой папке проекта
project_path = '/home/rumiantseva/web_rumiantseva_4sem'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.chdir(project_path)

from app.main import app as application  # обязательно ПЕРЕИМЕНОВАТЬ в 'application'
