import click
from flask.cli import with_appcontext
from .extensions import db

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Создание таблиц в БД"""
    from . import models
    db.create_all()
    click.echo('База данных инициализирована')

def init_app(app):
    app.cli.add_command(init_db_command) 