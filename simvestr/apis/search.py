import requests
from flask import jsonify
from flask_restx import Resource, Namespace, fields

from simvestr.helpers.auth import requires_auth
from simvestr.helpers.search import search
from simvestr.models import Stock, db

api = Namespace("search", description="Search stocks")


@api.route("/exchange/<string:exchange>")
class ExchangeList(Resource):

    @requires_auth
    def get(self, exchange: str = "US"):
        uri = search(source_api="finnhub", query="exchange", arg=exchange)
        r = requests.get(uri)
        return r.json()


quote_model = api.model(
    "Quote",
    {
        "o": fields.Float,
        "h": fields.Float,
        "l": fields.Float,
        "c": fields.Float,
        "pc": fields.Float,
        "t": fields.Integer,
    },
)
base_symbol_model = api.model(
    "Symbol",
    {
        "type": fields.String,
        "symbol": fields.String,
        "display_symbol": fields.String,
        "name": fields.String,
    },
)
details_model = api.model(
    "Details",
    {
        "type": fields.String,
        "symbol": fields.String,
        "name": fields.String,
        "industry": fields.String,
        "exchange": fields.String,
        "logo": fields.String,
        "marketCapitalization": fields.Float,
        "quote": fields.Nested(quote_model, skip_none=False),
    },
)


@api.route("/details/<string:stock_symbol>")
class StockDetails(Resource):
    @requires_auth
    @api.param("stock_symbol", "Stock or crypto symbol to be searched")
    @api.response(200, "Success")
    @api.response(404, "Symbol not found")
    @api.doc(
        model="Details", description="Gets details for the specified stock",
    )
    def get(self, stock_symbol: str = "AAPL"):
        # Since we are fetching from finnhub we need to fetch anyway, so why hit the DB at all?
        details = search(source_api="finnhub", query="profile", arg=stock_symbol)
        quote = search(source_api="finnhub", query="quote", arg=stock_symbol)
        # This can be STOCK or CRYPTO, for now only handle STOCK
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
                    "message": "Symbol not found. Incorrect symbol, check spelling.",
                },
                404,
            )


@api.route("/<string:name>")
class StockSearch(Resource):
    @requires_auth
    def get(self, name: str = "AAPL"):
        stock_q = Stock.query.filter(db.or_(
            Stock.display_symbol.ilike(name + "%"),
            Stock.name.ilike(name + "%")
        )).all()
        return [
            dict(symbol=s.symbol, display_symbol=s.display_symbol, name=s.name, )
            for s in stock_q
        ]


@api.route("/symbols")
class StockSymbols(Resource):
    @requires_auth
    def get(self):
        stock_q = Stock.query.all()
        return [
            dict(symbol=s.symbol, display_symbol=s.display_symbol, name=s.name, )
            for s in stock_q
        ]
