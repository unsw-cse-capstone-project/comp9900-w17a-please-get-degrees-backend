import requests
import datetime

from flask import jsonify
from flask_restx import Resource, Namespace, fields, reqparse

from simvestr.helpers.auth import requires_auth
from simvestr.helpers.search import search
from simvestr.models import Stock, db

api = Namespace("search", description="Search stocks")


@api.route("/exchange/<string:exchange>")
class ExchangeList(Resource):

    @requires_auth
    def get(self, exchange: str = "US"):
        uri = search(source_api="finnhub", query="exchange", arg=exchange)
        return uri


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
    # @api.param("stock_symbol", "Stock or crypto symbol to be searched") #this hangs the search and I dont know why
    @api.response(200, "Success")
    @api.response(404, "Symbol not found")
    @api.doc(
        model="Details", description="Gets details for the specified stock",
    )
    def get(self, stock_symbol):
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


candle_parser = reqparse.RequestParser()
candle_parser.add_argument("symbol", type=str, required=True, help="Stock symbol to search.")
candle_parser.add_argument("resolution", type=str, help="Resolution of data", default="D")
candle_parser.add_argument("from", type=float, help="UNIX timestamp. Interval initial value.")
candle_parser.add_argument("to", type=float, help="UNIX timestamp. Interval end value.")


@api.route("/candle")
@api.expect(candle_parser)
class Candles(Resource):
    @api.response(200, "Success")
    @api.response(404, "Symbol not found")
    @requires_auth
    def get(self):
        args = candle_parser.parse_args()
        args["symbol"] = args["symbol"].upper()
        current_unix_time = datetime.datetime.now().timestamp()

        if not args["from"]:
            args["from"] = int(current_unix_time - datetime.timedelta(weeks=1).total_seconds())

        if not args["to"]:
            args["to"] = int(current_unix_time)

        if not args["resolution"]:
            args["resolution"] = "60"
        print(args)
        candle = search(query="candle", arg=args)
        if candle["s"] == "no_data":
            return {"message": "Symbol not found or data, check inputs."}, 404

        return candle, 200
