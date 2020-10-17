import tempfile
import shutil
import os
import pytest
from simvestr import create_app
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path


@pytest.fixture
def app():
    temp_dir = tempfile.mkdtemp(prefix='temp_test_db_', dir=Path.cwd())
    db_fd, db_path = tempfile.mkstemp(suffix=".db", dir=temp_dir)
    db_path = Path(db_path)
    test_config = dict(
        TESTING=True,
        DATABASE=db_path.with_suffix('.sqlite'),
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}'
    )

    app = create_app(test_config)
    db = SQLAlchemy(app)

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