from flask_restx import Resource, Namespace, abort, reqparse

from simvestr.helpers.auth import requires_auth, get_user
from simvestr.helpers.search import get_details
from simvestr.helpers.watchlist import get_watchlist, in_watchlist
from simvestr.models import db, Stock, WatchlistItem
from simvestr.models.api_models import watchlist_item_model, watchlist_model, base_symbol

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

api.models[base_symbol.name] = base_symbol
api.models[watchlist_item_model.name] = watchlist_item_model
api.models[watchlist_model.name] = watchlist_model

watchlist_parser = reqparse.RequestParser()
watchlist_parser.add_argument("symbol", type=str)


@api.route("")
class Watchlist(Resource):
    # @api.param('watchlist_id', 'Stock or crypto symbol to be searched')
    @api.response(200, "Success")
    @api.doc(
        description="Gets details for the specified stock",
        security=["TOKEN-BASED"],
        model=watchlist_model,
    )
    @api.marshal_with(watchlist_model)
    @requires_auth
    def get(self):
        user = get_user()
        watchlist_list = get_watchlist(user)
        return watchlist_list, 200


    @api.marshal_with(base_symbol,)
    @api.response(200, "Entry in watchlist")
    @api.response(201, "Entry created")
    @api.response(404, "Symbol not found")
    @api.doc(
        description="Gets details for the specified stock",
        security=["TOKEN-BASED"],
        body=base_symbol,
    )
    @requires_auth
    def post(self):
        args = watchlist_parser.parse_args()
        symbol = args["symbol"].upper()

        # Run this to check if in the database or exisits. Will add it if not already there
        get_details(symbol)

        user = get_user()



        if not in_watchlist(symbol, user):
            watchlist_item =  WatchlistItem(watchlist_id=user.watchlist.id, stock_symbol=symbol,)
            user.watchlist.watchlist_items.append(
                watchlist_item
            )
            db.session.add(watchlist_item)
            db.session.commit()
            return {"symbol": symbol}, 201
        else:
            return {"symbol": symbol}, 200

    @api.response(200, "Not in watchlist")
    @api.response(201, "Removed from watchlist")
    @api.response(404, "Symbol not found")
    @api.doc(
        description="Gets details for the specified stock",
        security=["TOKEN-BASED"],
        body=base_symbol
    )
    @api.marshal_with(base_symbol)
    @requires_auth
    def delete(self,):
        user = get_user()
        args = watchlist_parser.parse_args()
        symbol = args["symbol"].upper()

        # Run this to check if in the database or exists. Will add it if not already there
        get_details(symbol)

        if in_watchlist(symbol, user):
            items_to_remove = [item for item in user.watchlist.watchlist_items if item.stock_symbol == symbol]
            user.watchlist.watchlist_items.remove(*items_to_remove)
            db.session.commit()
            return {"symbol": symbol}, 201
        else:
            return {"symbol": symbol}, 200
