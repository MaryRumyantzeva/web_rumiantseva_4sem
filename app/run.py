import logging
logging.getLogger('faker').setLevel(logging.ERROR)  # или logging.CRITICAL для полного отключения

from app.main import app

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, app, use_reloader=True, use_debugger=True)