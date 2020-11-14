from flask_restx import Resource, Namespace, reqparse, abort
from simvestr.helpers.auth import get_user, requires_auth
from simvestr.models import User, Portfolio, PortfolioPrice, Transaction, Watchlist, db
from sqlalchemy.sql import select
from flask import jsonify

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
        watch = user.watchlist
        port = user.portfolio

        for pp in PortfolioPrice.query.filter_by(portfolio_id=port.id).all() :
            PortfolioPrice.query.filter_by(id=pp.id).delete()
        for tr in Transaction.query.filter_by(portfolio_id=port.id).all() :
            Transaction.query.filter_by(id=pp.id).delete()

        User.query.filter_by(id=user.id).delete()
        Watchlist.query.filter_by(id=watch.id).delete()
        Portfolio.query.filter_by(id=port.id).delete()       

        db.session.commit()

        @after_this_request
        def set_cookie_value(response):
            response.delete_cookie("token")
            return response
      
        return (
            {"message": "Account Deleted", },
            200,
        )
        # user = User.query.filter_by(id=4).first()
        # watch = user.watchlist
        # port = user.portfolio
        # test =  str(user.id) + " "+ str(watch.id) + " "+ str(port.id) + " "
        # for pp in PortfolioPrice.query.filter_by(portfolio_id=port.id).all() :
        #     test = test + str(pp.id) + " "
        # for tr in Transaction.query.filter_by(portfolio_id=port.id).all() :
        #     test = test + str(tr.id) + " "
        #return test


    
    