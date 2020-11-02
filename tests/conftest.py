import tempfile
import shutil
import os
import pytest
from simvestr import create_app
from simvestr.helpers.db import init_db, db
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

API_URL = "/api/v1"

@pytest.fixture
def app():
    temp_dir = tempfile.mkdtemp(prefix="temp_test_db_", dir=Path.cwd())
    db_fd, db_path = tempfile.mkstemp(suffix=".db", dir=temp_dir)
    db_path = Path(db_path)
    test_config = dict(
        TESTING=True,
        DATABASE=db_path.with_suffix(".sqlite"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}"
    )

    app = create_app(test_config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    yield app

    os.close(db_fd)
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def test_db(app):
    return SQLAlchemy(app)


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='test@testmail.com', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': email, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
