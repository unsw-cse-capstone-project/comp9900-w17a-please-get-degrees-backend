from flask_restx import Resource, Namespace,reqparse
from ..models import User, Watchlist, Stock
from flask import current_app, jsonify
import requests
api = Namespace('Search', description='Search stocks')

@api.route('/<string:exchange>')
@api.param('exchange', 'The exchange to query for stocks')
class StockList(Resource):
    def get(self, exchange: str = 'US'):
        SYMBOL_ALL_API =  f'https://finnhub.io/api/v1/stock/symbol?exchange={exchange}&token={current_app.config["FINNHUB_API_KEY"]}'

        r = requests.get(SYMBOL_ALL_API)
        return r.json()


@api.route('/symbol/{stock_symbol}')
@api.param('stock_symbol', 'The stock symbol of the searched stock')
class StockQuery(Resource):
    def get(self, stock_symbol: str='AAPL'):
        PROFILE_API = f'https://finnhub.io/api/v1/stock/profile2?symbol={stock_symbol}&token={current_app.config["FINNHUB_API_KEY"]}'
        r = requests.get(PROFILE_API)
        return r.json()