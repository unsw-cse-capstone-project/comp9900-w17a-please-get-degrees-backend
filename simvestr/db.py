# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from flask import current_app, g
import click
from flask.cli import with_appcontext
from simvestr.models import db

# Defines setup and tear down the database

def get_db():
    if 'db' not in g:
        g.db = db.init_app(current_app)
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# @click.command('init-db')
# @with_appcontext
def init_db():
    db = get_db()
    db.create_all()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
