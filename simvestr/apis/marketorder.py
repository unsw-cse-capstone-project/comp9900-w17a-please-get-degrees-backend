# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 11:23:31 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace, abort
from ..models import User, Watchlist, Stock, Portfolio, PortfolioPrice, Transaction
from simvestr.models import db
from sqlalchemy.sql import func
from .auth import requires_auth, get_email

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
        # "user_id": fields.Integer,
        # "portfolio_id": fields.Integer,
        "symbol": fields.String,
        "quote": fields.Float,
        "trade_type": fields.String,
        "quantity": fields.Integer,
    },
)
trade_parser = reqparse.RequestParser()
# trade_parser.add_argument("user_id", type=str)
# trade_parser.add_argument("portfolio_id", type=str)
trade_parser.add_argument("symbol", type=str)
trade_parser.add_argument("quote", type=float)
trade_parser.add_argument("trade_type", type=str)
trade_parser.add_argument("quantity", type=int)


def commit_transaction(
    user_id, portfolio_id, symbol, quote, trade_type, total_quantity, fee
):
    new_transaction = Transaction(
        user_id=user_id,
        portfolio_id=portfolio_id,
        symbol=symbol,
        quote=quote,
        trade_type=trade_type,
        quantity=total_quantity,
        fee=fee,
    )
    db.session.add(new_transaction)
    db.session.commit()


@api.route("")
class TradeStock(Resource):
    @api.response(200, "Successful")
    @api.response(449, "User doesn't exist")
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
        symbol = args.get("symbol")
        quote = args.get("quote")
        trade_type = args.get("trade_type")
        quantity = args.get("quantity")

        # get user details from token
        try:
            email = get_email()
        except Exception as e:
            abort(401, e)

        user = User.query.filter_by(email_id=email).first()
        portfolio_id = user.id
        portfolio_user = Portfolio.query.filter_by(id=user.id).all()
        portfolio_price_user = PortfolioPrice.query.filter_by(
            portfolio_id=user.id
        ).first()

        if not user:
            return ({"error": True, "message": "User doesn't exist"}, 449)
        if not portfolio_user:
            return ({"error": True, "message": "Portfolio doesn't exist"}, 601)
        if not portfolio_price_user:
            return ({"error": True, "message": "Portfolio Price doesn't exist"}, 602)

        fee = 0

        # --------------- Buy ---------------- #
        if (
            trade_type == "buy"
        ):  # check if user even has enough money to buy this stock quantity
            new_close_balance = portfolio_price_user.close_balance - (
                (quote * quantity) + fee
            )
            if new_close_balance < 0:
                return ({"error": True, "message": "Insufficiant funds"}, 650)
            total_quantity = quantity
            # find total quantity of stocks for symbol, if owned previously
            check_stock = Transaction.query.filter_by(
                user_id=user.id,
                portfolio_id=portfolio_id,
                symbol=symbol,
                trade_type="settled",
            ).all()
            if check_stock:
                total_quantity = quantity + check_stock[-1].quantity
                commit_transaction(
                    user.id, portfolio_id, symbol, quote, "settled", total_quantity, fee
                )
            else:
                commit_transaction(
                    user.id, portfolio_id, symbol, quote, "settled", total_quantity, fee
                )
        # ------------- Buy-ends ------------- #

        # --------------- Sell --------------- #
        if (
            trade_type == "sell"
        ):  # check if user owns this stock first, then the quantity he's trying to sell should'nt be more than he owns
            # check_stock = Transaction.query.with_entities (func.sum(Transaction.quantity).label('sum')). \
            #             filter_by(user_id=user_id, portfolio_id=portfolio_id, symbol=symbol).first()
            check_stock = Transaction.query.filter_by(
                user_id=user.id,
                portfolio_id=portfolio_id,
                symbol=symbol,
                trade_type="settled",
            ).all()
            if not check_stock:
                return (
                    {"error": True, "message": "You currently don't own this stock"},
                    603,
                )
            # check if selling more stocks than owned
            total_quantity = check_stock[-1].quantity - quantity
            if total_quantity < 0:
                return (
                    {
                        "error": True,
                        "message": "Insufficient quantity of funds to sell",
                    },
                    651,
                )
            commit_transaction(
                user.id, portfolio_id, symbol, quote, "settled", total_quantity, fee
            )
            new_close_balance = portfolio_price_user.close_balance + (
                (quote * quantity) + fee
            )
        # -------------- Sell-ends ----------- #

        portfolio_price_user.close_balance = (
            new_close_balance  # update user's balance after trade
        )
        print(user.id)
        new_transaction = Transaction(
            user_id=user.id,
            portfolio_id=portfolio_id,
            symbol=symbol,
            quote=quote,
            trade_type=trade_type,
            quantity=quantity,
            fee=fee,
        )

        db.session.add(new_transaction)
        db.session.commit()
        # Want to return a valid payload - i.e. return payload to confirm what we have done is correct
        return ({"error": False, "message": "Transaction Completed!"}, 200)
