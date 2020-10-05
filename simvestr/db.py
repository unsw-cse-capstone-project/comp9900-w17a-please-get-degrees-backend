from pathlib import Path
import pandas as pd
from flask import current_app, g
import click
from flask.cli import with_appcontext
from simvestr.models import db

# Defines setup and tear down the database

def get_db():
    if 'db' not in g:
        db.init_app(current_app)
        g.db = db

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.create_all()


def load_dummy():
    from .models import User
    db = get_db()
    user_data_path = Path.cwd() / 'tests' / 'test_data_user.xlsx'
    user_df = pd.read_excel(user_data_path)
    user_df.columns = user_df.columns.str.lower()
    db.session.bulk_insert_mappings(
        User,
        user_df.to_dict(orient="records")
    )
    db.session.commit()
    db.session.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
