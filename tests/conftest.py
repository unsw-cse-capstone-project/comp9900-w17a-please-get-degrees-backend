import os
import shutil
import tempfile
from pathlib import Path

import pytest
from flask_sqlalchemy import SQLAlchemy

from simvestr import create_app
from simvestr.helpers.db import db
from simvestr.helpers.search import search

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


# to use later, need to correct
class AuthActions(object):
    def __init__(self, client, email="test@test.com", password="pass1234",
                 first_name="test_first", last_name="test_last"):
        self._client = client
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def sign_up(self, ):
        new_user = {
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

        return self._client.post(
            "/".join([API_URL, "signup"]),
            data=new_user
        )

    def login(self, ):
        return self._client.post(
            "/".join([API_URL, "login"]),
            data={
                "email": self.email,
                "password": self.password,
            }
        )

    def logout(self):
        return self._client.get(
            "/".join([API_URL, "logout"]),
        )

    @property
    def name(self):
        return " ".join([self.first_name, self.last_name])


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def client_new_user(client):
    new_user = {
        "email": "test@test.com",
        "password": "pass1234",
        "first_name": "test",
        "last_name": "register"
    }
    client.post(
        "/".join([API_URL, "signup"]), data=new_user
    )
    return client


class NewUser(AuthActions):
    def __init__(self, client, email="test@test.com", password="pass1234", first_name="test_first",
                 last_name="test_last"):

        super().__init__(client, email, password, first_name, last_name)
        self.sign_up()
        self.login()

    def buy(self, symbol="AAPL", quote=None, quantity=15, ):
        if not quote:
            quote = search(query="quote", arg=symbol)
        buy = {
            "symbol": symbol,
            "quote": quote,
            "trade_type": "buy",
            "quantity": quantity,
        }

        self._client.post(
            "/".join([API_URL, "marketorder", ]),
            json=buy
        )

    def sell(self, symbol="AAPL", quote=None, quantity=1, ):
        if not quote:
            quote = search(query="quote", arg=symbol)
        sell = {
            "symbol": symbol,
            "quote": quote,
            "trade_type": "sell",
            "quantity": quantity,
        }

        self._client.post(
            "/".join([API_URL, "marketorder", ]),
            json=sell
        )


@pytest.fixture
def registered_user(client):
    return NewUser(client)
