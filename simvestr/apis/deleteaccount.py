from flask_restx import Resource, Namespace, reqparse, abort
from simvestr.helpers.auth import get_user, requires_auth
from simvestr.models import User, Portfolio, PortfolioPrice, Transaction, Watchlist, db
from simvestr.apis.logout import Token
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


@api.route("")
class DeleteAccount(Resource):
    @requires_auth
    @api.response(200, "Successful")
    @api.doc(
        description="delete user account",
    )
    def get(self):
        user = get_user()
        watch = user.watchlist
        port = user.portfolio

        for pp in PortfolioPrice.query.filter_by(portfolio_id=port.id).all() :
            PortfolioPrice.query.filter_by(id=pp.id).delete()
        for tr in Transaction.query.filter_by(portfolio_id=port.id).all() :
            Transaction.query.filter_by(id=tr.id).delete()

        User.query.filter_by(id=user.id).delete()
        Watchlist.query.filter_by(id=watch.id).delete()
        Portfolio.query.filter_by(id=port.id).delete()       

        db.session.commit()
        Token.get(self)
     
        return 200
