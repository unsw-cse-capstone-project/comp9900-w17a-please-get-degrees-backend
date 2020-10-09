from simvestr import create_app
from simvestr.db import init_db, load_dummy

app = create_app()

with app.app_context():
    init_db()
    load_dummy()