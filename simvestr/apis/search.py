import datetime

from flask import jsonify
from flask_restx import Resource, Namespace, reqparse

from simvestr.helpers.auth import requires_auth
from simvestr.helpers.search import search, get_details
from simvestr.models import Stock, db
from simvestr.models.api_models import candle_model, details_model, quote_model, search_name_model

api = Namespace("search", description="Search stocks")

api.models[quote_model.name] = quote_model
api.models[candle_model.name] = candle_model
api.models[details_model.name] = details_model
api.models[search_name_model.name] = search_name_model

@api.route("/details/<string:stock_symbol>")
class StockDetails(Resource):
    @requires_auth
    @api.response(200, "Success")
    @api.response(404, "Symbol not found")
    @api.doc(
        id="stock_details",
        model=details_model,
        description="Gets details for the specified stock",
        params={"stock_symbol": "The stock symbol associated with the company"},
    )
    @api.marshal_with(details_model)
    def get(self, stock_symbol):
        payload = get_details(stock_symbol.upper())
        return payload, 200



@api.route("/<string:name>")
class StockSearch(Resource):
    @api.doc(
        description="Partial name search for stocks and crypto.",
        model=search_name_model,
        params={"name": "The name or partial name of the stock symbol or company name"},
    )
    @api.marshal_with(search_name_model)
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

candle_parser = reqparse.RequestParser()
candle_parser.add_argument("symbol", type=str, required=True, help="Stock symbol to search.")
candle_parser.add_argument("resolution", type=str, help="Resolution of data", default="D", choices=("1", "5", "15", "30", "60", "D", "W", "M",))
candle_parser.add_argument("from", type=int, help="UNIX timestamp. Interval initial value.")
candle_parser.add_argument("to", type=int, help="UNIX timestamp. Interval end value.")


@api.route("/candle")
@api.expect(candle_parser)
class Candles(Resource):
    @api.response(200, "Success")
    @api.response(404, "Symbol not found")
    @api.doc(
        model=candle_model,
        description="Candles for a stock over a timeframe",
    )
    @api.marshal_with(candle_model)
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

        candle = search(query="candle", arg=args)
        if candle["s"] == "no_data":
            return {"message": "Symbol not found or data unavailable for that resolution, check inputs and try again."}, 404

        return candle, 200
