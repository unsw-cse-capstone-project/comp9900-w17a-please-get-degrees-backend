# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 11:23:31 2020

@author: Kovid
"""
from flask import current_app
from flask_restx import Resource, reqparse, Namespace, abort

from simvestr.helpers.auth import requires_auth, get_user
from simvestr.helpers.marketorder import check_price
from simvestr.helpers.portfolio import stock_balance
from simvestr.models import db, Transaction, Stock
from simvestr.models.api_models import market_order_model

api = Namespace(
    "marketorder",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="Buying and selling stocks",
    title="Simvestr",
    description="Back-end API for placing market-orders",
)

api.models[market_order_model.name] = market_order_model

trade_parser = reqparse.RequestParser()
trade_parser.add_argument("symbol", type=str)
trade_parser.add_argument("quote", type=float)
trade_parser.add_argument("trade_type", type=str)
trade_parser.add_argument("quantity", type=int)


@api.route("")
class TradeStock(Resource):
    @api.response(200, "Successful")
    @api.response(400, "Bad Request")
    @api.response(422, "Unprocessable Entity")
    @api.response(416, "Requested Range Not Satisfiable")
    @api.response(417, "Expectation Failed")
    @api.doc(model="Market Order", body=market_order_model, description="Places a market order")
    @api.marshal_with(market_order_model, code=200)
    @requires_auth
    def post(self):
        args = trade_parser.parse_args()
        symbol: str = args.get("symbol")
        quote = args.get("quote")
        trade_type = args.get("trade_type")
        quantity = args.get("quantity")
        symbol = symbol.upper()  # TODO: Need wrapper function to automatically uppercase the input

        user = get_user()  # get user details from token

        variation, slippage = check_price(symbol, quote)
        if variation:
            return abort(417, "Current price has changed, can't commit this transaction")

        stock = Stock.query.filter_by(symbol=symbol).first()
        fee = 0

        if quantity < 1:
            return abort(400, f"Quantity should be an integer value greater than 0. Given {quantity}")

        quantity = -quantity if trade_type == "sell" else quantity

        # --- Buy --- #
        if quantity > 0:  # check if user even has enough money to buy this stock quantity
            balance_adjustment = ((quote * quantity) + fee)
            if user.portfolio.balance - balance_adjustment < 0:
                return abort(417, "Insufficient funds")

            if stock not in user.portfolio.stocks:
                user.portfolio.stocks.append(stock)

        # --- Sell --- #
        elif quantity < 0:  # check if user owns this stock first, then the quantity he's
            check_stock = stock_balance(user, symbol)

            if not check_stock:
                return abort(417, "You currently don't own this stock")

            if check_stock[0] + quantity < 0:
                return abort(417, "Insufficient quantity of stock to sell")

            if check_stock[0] + quantity == 0:
                user.portfolio.stocks.remove(stock)

            balance_adjustment = (quote * quantity) + fee
        else:
            return abort(422, f"Invalid quantity. Quantity must be a non zero integer. Received {quantity}")

        stock.last_quote = quote

        user.portfolio.balance -= balance_adjustment  # update user's balance after trade
        # --- Sell-ends --- #

        new_transaction = Transaction(
            portfolio_id=user.portfolio.id,
            symbol=symbol,
            quote=quote,
            quantity=quantity,
            fee=fee,
        )

        db.session.add(new_transaction)
        db.session.commit()

        return dict(symbol=symbol, quote=quote, quantity=quantity, trade_type=trade_type, ), 200
        # return dict(symbol=symbol, quote=quote, quantity=quantity, trade_type=trade_type, slippage=slippage ), 200
