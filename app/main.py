import os
import sys
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Flask

# Создаем основное приложение
main_app = Flask(__name__)
main_app.config['SECRET_KEY'] = 'f038a541489b89f81762d12edfdd03835ceea10cfb3cdbdabfbfa0f48b0d4803'
main_app.config['DEBUG'] = True

# Импортируем приложения (теперь с абсолютными путями)
#from app.lab1.app import app as lab1_app
#from app.lab2.app import app as lab2_app
#from app.lab3.app import app as lab3_app
from app.kp.app import app as kp_app
from app.exam.app import app as exam_app

# Настройка маршрутизации
app = DispatcherMiddleware(main_app, {
    '/kp': kp_app,
    '/exam': exam_app,
    #'/lab1': lab1_app,
    #'/lab2': lab2_app,
    #'/lab3': lab3_app
})




@main_app.route('/')
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Румянцева веб</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        .nav { background: #f5f5f5; padding: 15px; border-radius: 5px; }
        a { display: block; margin: 10px 0; color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Добро пожаловать в Румянцева веб 4сем!</h1>
    <div class="nav">
        <h2>Доступные разделы:</h2>
        <a href="/kp/">Курсач</a>
        
        <a href="/exam/">Экзаменационный проект</a>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, app, use_reloader=True, use_debugger=True)