from investr import create_app

app = create_app()


with app.app_context():
    from investr.models.db import db
    db.create_all()
