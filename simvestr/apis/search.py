import requests

from flask_restx import Resource, Namespace, reqparse, fields
from flask import jsonify, current_app

from simvestr.models import User, Watchlist, Stock
from simvestr.helpers.search import search, STOCK_TYPE_MAP

api = Namespace("search", description="Search stocks")


@api.route("/exchange/<string:exchange>")
class ExchangeList(Resource):
    def get(self, exchange: str = "US"):
        uri = search(source_api='finnhub' ,query="exchange", arg=exchange)
        r = requests.get(uri)
        return r.json()


quote_model = api.model(
    "Quote", {
        "o": fields.Float,
        "h": fields.Float,
        "l": fields.Float,
        "c": fields.Float,
        "pc": fields.Float,
    }
)
base_symbol_model = api.model(
    "Symbol", {
        "type": fields.String,
        "symbol": fields.String,
        "display_symbol": fields.String,
        "name": fields.String,
    }
)
symbol_model = api.model(
    "Symbol", {
        "type": fields.String,
        "symbol": fields.String,
        "name": fields.String,
        "exchage": fields.String,
        "marketCapitalization": fields.Integer,
        "quote": fields.Nested(quote_model, skip_none=False)
    }
)


@api.route("/details/<string:stock_symbol>")
class StockDetails(Resource):
    response_fields = [
        "type",
        "symbol",
        "name",
        "exchage",
        "marketCapitalization",
        "quote",
    ]
    @api.marshal_with(symbol_model)
    @api.param('stock_symbol', 'Stock or crypto symbol to be searched')
    @api.response(200, "Success")
    @api.response(404, "Symbol not found")
    @api.doc(description="Gets details for the specified stock",)
    def get(self, stock_symbol: str = "APPL"):

        # First hit the db to see if we've got the data
        stock_q = Stock.query.filter_by(display_symbol=stock_symbol.upper()).all()

        stockType = STOCK_TYPE_MAP[False]
        print("hit the API")
        if not stock_q:
            uri = search(source_api='finnhub' ,query="profile", arg=stock_symbol)
            stock = requests.get(uri).json()

            # If not, it will hit the crypto api to see if the stock is there.
            if not stock:
                stockType = STOCK_TYPE_MAP[True]
                uri = search(source_api='finnhub' ,
                    query="profile",
                    arg=stock_symbol
                )
                stock = requests.get(uri).json()
        else:
            return [
                dict(
                    type=STOCK_TYPE_MAP[s.is_crypto],
                    symbol=s.display_symbol,
                    name=s.name,
                    exchage=s.exchange,
                    marketCapitalization=requests.get(
                        search(source_api='finnhub' ,query="profile", arg=s.symbol)
                    ).json()["marketCapitalization"],
                    quote=requests.get(
                        search(source_api='finnhub' ,query="quote", arg=stock_symbol)
                    ).json(),
                )
                for s in stock_q
            ]

        # if it cant be found, error out
        if not stock:
            return {
                "error": True,
                "message": "Symbol not found. Incorrect symbol, check spelling.",
            }
        uri = search(source_api='finnhub' ,query="quote", arg=stock_symbol)
        r = requests.get(uri).json()
        stock.update({"type": stockType, "quote": r})
        stock = {k: v for k, v in stock if k in StockDetails.response_fields}
        return stock


# @api.route("/<string:name>")
# class StockSearch(Resource):
#     def get(self, name: str = "APPL"):
#         stock_q = Stock.query.filter(Stock.display_symbol.ilike(name + "%")).all()
#         return [
#             dict(symbol=s.symbol, display_symbol=s.display_symbol, name=s.name, )
#             for s in stock_q
#         ]


@api.route("/symbols")
class StockSymbols(Resource):
    def get(self, exchange: str = "US"):
        stock_q = Stock.query.all()
        return [
            dict(symbol=s.symbol, display_symbol=s.display_symbol, name=s.name, )
            for s in stock_q
        ]
