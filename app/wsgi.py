import sys
import os

# путь к корневой папке проекта
project_path = r'C:\Users\rumya\OneDrive\Рабочий стол\вуз\4сем\веб\application_dispatching_example'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.chdir(project_path)

from app.main import app as application  # обязательно ПЕРЕИМЕНОВАТЬ в 'application'
