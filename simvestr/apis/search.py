import datetime

from flask import jsonify
from flask_restx import Resource, Namespace, reqparse

from simvestr.helpers.auth import requires_auth
from simvestr.helpers.search import search
from simvestr.models import Stock, db
from simvestr.helpers.api_models import quote_model, details_model

api = Namespace("search", description="Search stocks")

api.models[quote_model.name] = quote_model # do we need these?
api.models[details_model.name] = details_model

@api.route("/exchange/<string:exchange>")
class ExchangeList(Resource):

    @requires_auth
    def get(self, exchange: str = "US"):
        uri = search(source_api="finnhub", query="exchange", arg=exchange)
        return uri

@api.route("/details/<string:stock_symbol>")
class StockDetails(Resource):
    @requires_auth
    @api.response(200, "Success")
    @api.response(404, "Symbol not found")
    @api.doc(
        id="stock_details",
        model="Stock Details",
        body=details_model,
        description="Gets details for the specified stock",
        params={"stock_symbol": "The stock symbol associated with the company"},
    )
    def get(self, stock_symbol):
        # Since we are fetching from finnhub we need to fetch anyway, so why hit the DB at all?
        # Remebered why we need to hit db - we have to check the exchange the stock is in to make a choice between crypto and regular stock.

        stock = Stock.query.filter_by(symbol=stock_symbol)
        stock = [] #teemporary bug fix - need to implement crypto checking logic
        if not stock:
            details = search(source_api="finnhub", query="profile", arg=stock_symbol)
            quote = search(source_api="finnhub", query="quote", arg=stock_symbol)
        # This can be STOCK or CRYPTO, for now only handle STOCK
        stockType = "STOCK"
        if details and quote: #Gives an error - local variable 'details' referenced before assignment
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
    @api.doc(
        params={"name": "The name or partial name of the stock symbol or company name"},
    )
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
candle_parser.add_argument("from", type=int, help="UNIX timestamp. Interval initial value.")
candle_parser.add_argument("to", type=int, help="UNIX timestamp. Interval end value.")


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
