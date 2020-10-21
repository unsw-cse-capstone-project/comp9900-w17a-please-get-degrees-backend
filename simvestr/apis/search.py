from flask_restx import Resource, Namespace
from ..models import User, Watchlist, Stock
from flask import jsonify, current_app
import requests

api = Namespace("search", description="Search stocks")


@api.route("/exchange/<string:exchange>")
class StockList(Resource):
    def get(self, exchange: str = "US"):
        SYMBOL_ALL_API = (
            lambda ex: f'https://finnhub.io/api/v1/stock/symbol?exchange={ex}&token={current_app.config["FINNHUB_API_KEY"]}'
        )

        r = requests.get(SYMBOL_ALL_API(exchange))
        return r.json()


@api.route("/symbol/<string:stock_symbol>")
class StockDetails(Resource):
    def get(self, stock_symbol: str = "APPL"):
        PROFILE_API = (
            lambda sym: f'https://finnhub.io/api/v1/stock/profile2?symbol={sym}&token={current_app.config["FINNHUB_API_KEY"]}'
        )
        stock = requests.get(PROFILE_API(stock_symbol)).json()
        QUOTE_API = (
            lambda sym: f'https://finnhub.io/api/v1/quote?symbol={sym}&token={current_app.config["FINNHUB_API_KEY"]}'
        )
        r = requests.get(QUOTE_API(stock_symbol)).json()
        stock.update({"quote": r})
        return jsonify(stock)


@api.route("/symbols")
class StockSymbols(Resource):
    def get(self, exchange: str = "US"):
        PROFILE_API = (
            lambda ex: f'https://finnhub.io/api/v1/stock/symbol?exchange={ex}&token={current_app.config["FINNHUB_API_KEY"]}'
        )
        stocks = requests.get(PROFILE_API(exchange)).json()
        payload = [stock["symbol"] for stock in stocks]
        return jsonify(payload)
