# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 11:23:31 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace

from simvestr.helpers.auth import requires_auth, get_user
from simvestr.helpers.portfolio import stock_balance
from simvestr.models import db, Transaction

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

trade_model = api.model(
    "MarketOrder",
    {
        "symbol": fields.String(
            required=True,
            description="Stock symbol for transaction",
            example="AAPL"
        ),
        "quote": fields.Float(
            required=True,
            description="Quote price per share of stock",
            example=1200
        ),
        "trade_type": fields.String(
            required=True,
            description="Stock symbol for transaction",
            example="buy",
            enum=[
                "buy",
                "sell"
            ]
        ),
        "quantity": fields.Integer(
            required=True,
            description="Quote price per share of stock",
            example=5
        ),
    },
)
trade_parser = reqparse.RequestParser()
trade_parser.add_argument("symbol", type=str)
trade_parser.add_argument("quote", type=float)
trade_parser.add_argument("trade_type", type=str)
trade_parser.add_argument("quantity", type=int)


@api.route("")
class TradeStock(Resource):
    @api.response(200, "Successful")
    @api.response(449, "User doesn't exist")
    @api.response(422, "Unprocessable Entity")
    @api.response(401, "Exception error")
    @api.response(601, "Portfolio doesn't exist")
    @api.response(602, "Portfolio Price doesn't exist")
    @api.response(603, "You currently don't own this stock")
    @api.response(650, "Insufficient funds")
    @api.response(651, "Insufficient quantity of funds to sell")
    @api.doc(model="MarketOrder", body=trade_model, description="Places a market order")
    @requires_auth
    def post(self):
        args = trade_parser.parse_args()
        symbol: str = args.get("symbol")
        quote = args.get("quote")
        trade_type = args.get("trade_type")
        quantity = args.get("quantity")
        symbol = symbol.upper()
        # get user details from token
        user = get_user()

        fee = 0
        quantity = -quantity if trade_type == "sell" else quantity

        # --------------- Buy ---------------- #
        if quantity > 0:  # check if user even has enough money to buy this stock quantity
            balance_adjustment = ((quote * quantity) + fee)
            if user.portfolio.portfolioprice[0].close_balance - balance_adjustment < 0:
                return {"message": "Insufficiant funds"}, 650

        # ------------- Buy-ends ------------- #

        # --------------- Sell --------------- #
        elif quantity < 0:  # check if user owns this stock first, then the quantity he's
            check_stock = stock_balance(user, symbol)

            print(check_stock)

            if not check_stock:
                return {"message": "You currently don't own this stock"}, 603

            if check_stock[0] + quantity < 0:
                return {"message": "Insufficient quantity of stock to sell"}, 651

            balance_adjustment = (quote * quantity) + fee
        else:
            return {"message": f"Invalid quantity. Quantity must be a non zero integer. Received {quantity}"}, 422

        user.portfolio.portfolioprice[0].close_balance -= balance_adjustment  # update user's balance after trade
        # -------------- Sell-ends ----------- #

        new_transaction = Transaction(
            # user_id=user.id,
            portfolio_id=user.portfolio.id,
            symbol=symbol,
            quote=quote,
            # trade_type=trade_type,
            quantity=quantity,
            fee=fee,
        )

        db.session.add(new_transaction)
        db.session.commit()

        return dict(symbol=symbol, quote=quote, quantity=quantity,), 200
