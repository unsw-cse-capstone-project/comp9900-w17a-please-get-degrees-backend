from simvestr import create_app

app = create_app()


with app.app_context():
    from simvestr.db import db
    db.create_all()
