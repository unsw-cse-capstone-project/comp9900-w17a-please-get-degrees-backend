from ..models import User, Watchlist, Stock
from simvestr.helpers.auth import requires_auth, get_email


from flask_restx import Resource, Namespace
from flask import current_app, request
import requests
authorizations={
        "TOKEN-BASED": {
            "name": "API-TOKEN",
            "in": "header",
            "type": "apiKey"
        }
    }
api = Namespace(
    'watchlist',
    authorizations=authorizations,
    security="TOKEN-BASED",
    description="Query , add and remove stocks from a users watch list."
)


@api.route('/<string:watchlist_id>')
class Watchlist(Resource):
    @api.param('watchlist_id', 'Stock or crypto symbol to be searched')
    @api.response(200, "Success")
    # @api.response(404, "Symbol not found")
    @api.doc(
        description="Gets details for the specified stock",
        security=["TOKEN-BASED"]
    )
    # @requires_auth
    def get(self, watchlist_id):
        email = get_email()
        user_id = User.query.filter_by(email_id=email)
        watchlist = Watchlist.query.filter_by()
        return

    # def delete(self, ):
    #     return

# @api.route('/<string:watchlist_id>/<string:symbol>')
# class WatchlistSingle(Resource):
#     @api.param('stock_symbol', 'Stock or crypto symbol to be searched')
#     @api.response(200, "Success")
#     @api.response(404, "Symbol not found")
#     @api.doc(description="Gets details for the specified stock", )
#     @requires_auth
#     def post(self, exchange: str = 'US'):
#
#         return
#
#     def delete(self, exchange: str = 'US'):
#
#         return


# @api.route('/<integer:watchlist_id>/<string:stock_symbol>')
# class WatchlistGlobal(Resource):
#     @requires_auth
#     def post(self, stock_symbol: str='APPL'):
#
#         return