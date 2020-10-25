from simvestr.models import db, User, Watchlist, Stock
from simvestr.helpers.auth import requires_auth, get_email
from simvestr.helpers.search import search
from collections import defaultdict
import requests

from flask_restx import Resource, Namespace, abort
from flask import current_app, request

authorizations = {
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


@api.route('/')
class WatchlistAll(Resource):
    # @api.param('watchlist_id', 'Stock or crypto symbol to be searched')
    @api.response(200, "Success")
    @api.doc(
        description="Gets details for the specified stock",
        security=["TOKEN-BASED"]
    )
    @requires_auth
    def get(self):
        # get user details from token
        try:
            email = get_email()
        except Exception as e:
            abort(401, e)
        print(email)
        user = User.query.filter_by(email_id=email).first()
        print(user)
        # watchlist = Watchlist.query.filter_by(user_id=user_id.id).all()
        watchlist = Watchlist.query.filter_by(
            user_id=user.id
        ).join(
            Stock,
            isouter=True,
        ).all()
        print(watchlist)
        watchlist_list = []
        for stock in watchlist:
            print(stock)
            watchlist_list.append(
                {
                    "symbol": stock.stock_symbol,
                    "name": stock.name,
                    "quote": search("finnhub", "quote", stock.stock_symbol)
                }
            )
        # Use this logic if we allow users to have multiple watch lsits.
        # watchlist_list = defaultdict(list)
        # for stock in watchlist:
        #     watchlist_list[stock.id].append(
        #         {
        #             "symbol": stock.stock_symbol
        #         }
        #     )
        return watchlist_list


def in_watchlist(symbol, user) -> bool:
    watched_stock = Watchlist.query.filter_by(user_id=user.id, stock_symbol=symbol).first()
    if watched_stock:
        return True
    return False


@api.route('/symbol/<string:symbol>')
class WatchlistPost(Resource):
    # @api.param('symbol', 'Stock or crypto symbol to be searched')

    @api.response(200, "Entry in watchlist")
    @api.response(201, "Entry created")
    @api.response(404, "Symbol not found")
    @api.doc(
        description="Gets details for the specified stock",
        security=["TOKEN-BASED"]
    )
    @requires_auth
    def post(self, symbol: str):
        try:
            email = get_email()
        except Exception as e:
            abort(401, e)
        user = User.query.filter_by(email_id=email).first()
        if not in_watchlist(symbol, user):
            watchlist = Watchlist(
                user_id=user.id,
                stock_symbol=symbol.upper()
            )
            db.session.add(watchlist)
            db.session.commit()

            return {
                       "message": f"{symbol} added to watchlist"
                   }, 201
        else:
            return

    @api.response(200, "Success")
    @api.response(404, "Symbol not found")
    @api.doc(
        description="Gets details for the specified stock",
        security=["TOKEN-BASED"]
    )
    @requires_auth
    def delete(self, symbol: str):
        try:
            email = get_email()
        except Exception as e:
            abort(401, e)
        user = User.query.filter_by(email_id=email).first()
        watchlist = Watchlist.query.filter_by(user_id=user.id, stock_symbol=symbol).first()
        if watchlist:
            db.session.delete(watchlist)
            db.session.commit()
            return f"{symbol} deleted from watchlist", 200
        else:
            return f"{symbol} not in watchlist", 404

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
