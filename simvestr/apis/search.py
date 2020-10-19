from flask_restx import Resource, Namespace
from ..models import User, Watchlist, Stock
from flask import jsonify, current_app
import requests
api = Namespace('Search', description='Search stocks')


@api.route('/<string:exchange>')
class StockList(Resource):
    def get(self, exchange: str = 'US'):
        SYMBOL_ALL_API = lambda \
            ex: f'https://finnhub.io/api/v1/stock/symbol?exchange={ex}&token={current_app.config["FINNHUB_API_KEY"]}'

        r = requests.get(SYMBOL_ALL_API(exchange))
        return r.json()


@api.route('/<string:stock_symbol>')
class StockQuery(Resource):
    def get(self, stock_symbol: str = 'APPL'):
        PROFILE_API = lambda \
            sym: f'https://finnhub.io/api/v1/stock/profile2?symbol={sym}&token={current_app.config["FINNHUB_API_KEY"]}'
        print(PROFILE_API(stock_symbol))
        r = requests.get(PROFILE_API(stock_symbol))
        return r.json()


@ api.route('/finnhub/<string:stock_symbol>')
class get_stock_finn(Resource):
    def get(self, stock_symbol: str = 'APPL'):
        PROFILE_API = lambda \
            sym: f'https://finnhub.io/api/v1/stock/profile2?symbol={sym}&token={current_app.config["FINNHUB_API_KEY"]}'
        stock = requests.get(PROFILE_API(stock_symbol)).json()
        PROFILE_API = lambda \
            sym: f'https://finnhub.io/api/v1/quote?symbol={sym}&token={current_app.config["FINNHUB_API_KEY"]}'
        r = requests.get(PROFILE_API(stock_symbol)).json()
        stock.update(r)
        return jsonify(stock)


@ api.route('/symbols/<string:exchange>')
class get_symbols(Resource):
    def get(self, exchange: str = 'US'):
        PROFILE_API = lambda \
            ex: f'https://finnhub.io/api/v1/stock/symbol?exchange={ex}&token={current_app.config["FINNHUB_API_KEY"]}'
        stocks = requests.get(PROFILE_API(exchange)).json()
        payload = []
        for stock in stocks:
            payload.append(stock['symbol'])
        return jsonify(payload)
