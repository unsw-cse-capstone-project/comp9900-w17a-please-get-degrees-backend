from ..models import User, Watchlist, Stock
from simvestr.helpers.auth import requires_auth


from flask_restx import Resource, Namespace
from flask import current_app
import requests
api = Namespace('Watchlist', description='Search stocks')


@api.route('/')
class Watchlist(Resource):
    @api.param('stock_symbol', 'Stock or crypto symbol to be searched')
    @api.response(200, "Success")
    @api.response(404, "Symbol not found")
    @api.doc(description="Gets details for the specified stock", )
    @requires_auth
    def get(self, ):
        return

    def delete(self, exchange: str = 'US'):
        return

@api.route('/<string:symbol>')
class WatchlistSingle(Resource):
    @api.param('stock_symbol', 'Stock or crypto symbol to be searched')
    @api.response(200, "Success")
    @api.response(404, "Symbol not found")
    @api.doc(description="Gets details for the specified stock", )
    @requires_auth
    def post(self, exchange: str = 'US'):

        return

    def delete(self, exchange: str = 'US'):

        return


@api.route('/<string:stock_symbol>')
class WatchlistGlobal(Resource):
    @requires_auth
    def post(self, stock_symbol: str='APPL'):

        return