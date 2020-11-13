from flask_restx import Resource, Namespace, reqparse, abort
from simvestr.helpers.auth import get_user, requires_auth
from simvestr.models import User, Portfolio, Watchlist, db
from sqlalchemy.sql import select

api = Namespace(
    "deleteaccount",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="Additional Feature - Delete Account",
    title="Simvestr",
    description="Back-end API for deleting users account",
)

@api.route("/")
class DeleteAccount(Resource):
    @requires_auth
    @api.response(200, "Successful")
    @api.doc(
        description="deletes users account, watchlist and portfolio",
        #model=delete_account_model,
    )
    def get(self):
        user = get_user()
        User.query.filter_by(id=user.id).delete()
        db.session.commit()
        return (
            {"message": "Account deleted", },
            200,
        )
    