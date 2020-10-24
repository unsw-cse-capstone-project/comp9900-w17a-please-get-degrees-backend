from flask_restx import Resource, Namespace, reqparse
from ..models import User, Watchlist, Stock
from flask import jsonify, current_app
import requests

api = Namespace("search", description="Search stocks")

FINNHUB_BASE = "https://finnhub.io/api/v1/"

QUERYS = dict(
    exchange="stock/symbol?exchange=",
    profile="stock/profile2?symbol=",
    quote="quote?symbol=",
)

STOCK_TYPE_MAP = {True: "CRYPTO", False: "STOCK"}


def finnhub_search(query: str, arg):
    token = f'&token={current_app.config["FINNHUB_API_KEY"]}'
    query_string = QUERYS[query]
    uri = f"{FINNHUB_BASE}{query_string}{arg}{token}"
    return uri


@api.route("/exchange/<string:exchange>")
class ExchangeList(Resource):
    def get(self, exchange: str = "US"):
        uri = finnhub_search(query="exchange", arg=exchange)
        r = requests.get(uri)
        return r.json()


@api.route("/details/<string:stock_symbol>")
class StockDetails(Resource):
    @api.response(200, "Success")
    @api.response(404, "Symbol not found")
    @api.doc(description="Gets details for the specified stock",)
    def get(self, stock_symbol: str = "APPL"):

        # Since we are fetching from finnhub we need to fetch anyway, so why hit the DB at all?
        details = requests.get(finnhub_search(query="profile", arg=stock_symbol)).json()
        quote = requests.get(finnhub_search(query="quote", arg=stock_symbol)).json()
        print(details)
        # This can be STOCK or CRYPTO
        stockType = "STOCK"
        if details and quote:
            stock = {
                "type": stockType,
                "symbol": details["ticker"],
                "name": details["name"],
                "industry": details["finnhubIndustry"],
                "exchange": details["exchange"],
                "logo": details["logo"],
                "marketCapitalization": details["marketCapitalization"],
                "quote": quote,
            }
            return jsonify(stock)
        else:
            return (
                {
                    "error": True,
                    "message": "Symbol not found. Incorrect symbol, check spelling.",
                },
                404,
            )


@api.route("/<string:name>")
class StockSearch(Resource):
    def get(self, name: str = "APPL"):
        stock_q = Stock.query.filter(Stock.display_symbol.ilike(name + "%")).all()
        return [
            dict(symbol=s.symbol, display_symbol=s.display_symbol, name=s.name,)
            for s in stock_q
        ]


@api.route("/symbols")
class StockSymbols(Resource):
    def get(self, exchange: str = "US"):
        stock_q = Stock.query.all()
        return [
            dict(symbol=s.symbol, display_symbol=s.display_symbol, name=s.name,)
            for s in stock_q
        ]
