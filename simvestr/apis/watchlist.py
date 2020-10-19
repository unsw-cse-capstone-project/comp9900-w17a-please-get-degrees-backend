from flask_restx import Resource, Namespace
from ..models import User, Watchlist, Stock
from flask import current_app
import requests
api = Namespace('Search', description='Search stocks')

@api.route('/<string:exchange>')
class Watchlist(Resource):
    def get(self, exchange: str = 'US'):

        return


@api.route('/<string:stock_symbol>')
class WatchlistAdd(Resource):
    def post(self, stock_symbol: str='APPL'):

        return