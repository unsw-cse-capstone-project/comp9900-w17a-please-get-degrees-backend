import pandas as pd
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


# class TestDB:
#     @classmethod
#     def setup_class(cls, app, test_db):
#         from simvestr.db import User
#         user_data_path = Path.cwd() / 'test_data_user.xlsx'
#         user_df = pd.read_excel(user_data_path)
#         with app.app_context():
#             test_db.session.bulk_insert_mappings(
#                 User,
#                 user_df.to_dict(orient="records")
#             )
#         cls.app = app
#         cls.db= test_db
#         cls.data = user_df
#
#
def test_bulk_create_user(app):
    db = SQLAlchemy(app)
    from simvestr.db import User

    user_data_path = Path.cwd() / 'test_data_user.xlsx'
    user_df = pd.read_excel(user_data_path)
    # db = SQLAlchemy(app)
    with app.app_context():
        db.session.bulk_insert_mappings(
            User,
            user_df.to_dict(orient="records")
        )

    with app.app_context():
        assert db.session.query(func.count(User.id)) == len(user_df)
