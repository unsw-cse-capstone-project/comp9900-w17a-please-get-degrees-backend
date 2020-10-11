from flask_restx import Resource, fields, reqparse, Namespace
from ..models import Stock
from flask import jsonify
from simvestr.models import db

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


@ api.route('/<symbol>')
class get_stock(Resource):
    def get(self, symbol):
        stock = Stock.query.get(symbol)
        return jsonify(stock=Stock.serialize(stock))


@ api.route('/all')
class get_stocks(Resource):
    def get(self):
        stocks = Stock.query.all()
        return jsonify(stocks=Stock.serialize_list(stocks))
