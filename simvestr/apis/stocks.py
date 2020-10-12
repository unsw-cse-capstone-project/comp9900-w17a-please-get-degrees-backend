from flask_restx import Resource, fields, reqparse, Namespace
from ..models import Stock
from flask import jsonify, make_response
from simvestr.models import db
import requests
import json

api = Namespace('Stocks', description='Demo api for querying stocks')


stock_parser = reqparse.RequestParser()
stock_parser.add_argument('symbol', type=str)
stock_parser.add_argument('name', type=str)
stock_parser.add_argument('currency', type=str)
stock_parser.add_argument('exchange', type=str)
stock_parser.add_argument('industry', type=str)
stock_parser.add_argument('country', type=str)


@api.route('/')
class put_pstock(Resource):
    @api.expect(stock_parser, validate=True)
    def put(self):
        args = stock_parser.parse_args()
        symbol = args.get('symbol')
        name = args.get('name')
        currency = args.get('currency')
        exchange = args.get('exchange')
        industry = args.get('industry')
        country = args.get('country')
        new_stock = Stock(
            symbol=symbol, name=name, currency=currency, exchange=exchange, industry=industry, country=country)
        db.session.add(new_stock)
        db.session.commit()
        return jsonify({'message': 'New stock created!'})

# gets stock data from simvestr database


@ api.route('/stored/<symbol>')
class get_stock(Resource):
    def get(self, symbol):
        stock = Stock.query.get(symbol)
        return jsonify(stock=Stock.serialize(stock))

# gets ALL data from simvestr database


@ api.route('/all')
class get_stocks(Resource):
    def get(self):
        stocks = Stock.query.all()
        return jsonify(stocks=Stock.serialize_list(stocks))

# Simon Test -- this populates the stocks table from finnhub
# @ api.route('/populate')
# class populate(Resource):
#     def get(self):

#         r = requests.get(
#             'https://finnhub.io/api/v1/stock/symbol?exchange=US&token=bu1uf5748v6sao5m33sg')
#         stocks = r.json()
#         Stock.query.delete()
#         for stock in stocks:
#             symbol = stock['symbol']
#             name = stock['symbol']+stock['description']
#             currency = stock['currency']
#             exchange = '-'
#             industry = stock['type']
#             country = '-'
#             new_stock = Stock(symbol=symbol, name=name, currency=currency,
#                               exchange=exchange, industry=industry, country=country)
#             db.session.add(new_stock)
#         db.session.commit()
#         return jsonify(stocks[1400])

# gets stock data from finnhub from a stock symbol


@ api.route('/finnhub/<symbol>')
class get_stock_finn(Resource):
    def get(self, symbol):
        r = requests.get(
            'https://finnhub.io/api/v1/stock/profile2?symbol='+symbol+'&token=bu22pqf48v6uohspr3p0')
        stock = r.json()
        r = requests.get(
            'https://finnhub.io/api/v1/quote?symbol='+symbol+'&token=bu22pqf48v6uohspr3p0')
        stock.update(r.json())

        return jsonify(stock)
