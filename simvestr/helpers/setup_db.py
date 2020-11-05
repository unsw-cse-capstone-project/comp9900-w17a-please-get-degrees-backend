from simvestr import create_app
from simvestr.helpers.db import init_db, load_dummy, delete_db

def setup_new_db():
    app = create_app()
    
    with app.app_context():
        delete_db()
        init_db()
        load_dummy()