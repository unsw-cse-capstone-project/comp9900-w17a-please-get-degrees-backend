
from werkzeug.security import generate_password_hash


from simvestr.models import User, db
from simvestr.helpers.db import make_salt


def change_password(user: User, password: str):
    user.salt = make_salt()
    user.password = generate_password_hash(password + user.salt, method="sha256")
    db.session.commit()