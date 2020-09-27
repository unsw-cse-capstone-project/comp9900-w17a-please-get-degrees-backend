import os
from pathlib import Path

from flask import Flask


def create_app(test_config=None):
    # create and configure the app

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=Path(app.instance_path) / 'investr.sqlite',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + str(Path(app.instance_path) / 'investr.db'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        Path(app.instance_path).mkdir(exist_ok=True)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Investr app'

    return app