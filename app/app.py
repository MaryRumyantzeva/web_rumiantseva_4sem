from werkzeug.middleware.dispatcher import DispatcherMiddleware
from lab1.app import app as lab1_app
from lab2.app import app as lab2_app
from lab3.app import app as lab3_app
#from app.root_app.test_ import app as root_app
from root_app.test_ import app as root_app

app = DispatcherMiddleware(root_app, {
    '/lab1': lab1_app,
    '/lab2': lab2_app,
    '/lab3': lab3_app
})
application = app
