# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 20:58:41 2020
@author: Kovid
"""

from flask_restx import Resource, Namespace, abort
from simvestr.models import User, Watchlist, Stock, Transaction
from simvestr.helpers.auth import get_email

api = Namespace(
    "view stocks",
    authorizations = {
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security = "TOKEN-BASED",
    default = "Buying and selling stocks",
    title = "Simvestr",
    description = "Demo api for querying owned stocks",
)
   

@api.route('/')
class StocksOwnedQuery(Resource):
    def get(self,):
        try:
            email = get_email()
        except Exception as e:
            abort(401, e)
        user = User.query.filter_by(email_id=email).first()

        # stocks = [t.symbol for t in Transaction.query.with_entities(Transaction.symbol).distinct()] # all distinct symbols
        
        #get disctinct stocks from transaction for user
        # stocks = Transaction.query.with_entities((Transaction.symbol).distinct())\
        #         .filter_by(trade_type = "settled", user_id = user_id).all()
        
        #get disctinct portfolios for user
        # portfolios = Transaction.query.with_entities((Transaction.portfolio_id).distinct())\
        #         .filter_by(trade_type = "settled", user_id = user_id).all()

        data = [dict(
            symbol=s.symbol,
            quantity=1
        ) for s in user.portfolio.stocks]

        # for p in portfolios_list:
        #     for s in stocks_list:
        #         check_stock = Transaction.query.filter_by(
        #             user_id = user_id, \
        #             portfolio_id = p, \
        #             symbol = s, \
        #             trade_type = "settled" \
        #         ).all()
        #         if check_stock:
        #             owned_stock = check_stock[-1]
        #             if owned_stock.quantity >= 1:
        #                 data[owned_stock.id] = dict(
        #                                 user_id = owned_stock.user_id,
        #                                 portfolio_id = owned_stock.portfolio_id,
        #                                 symbol = owned_stock.symbol,
        #                                 quote = owned_stock.quote,
        #                                 # trade_type = owned_stock.trade_type,
        #                                 # timestamp = str(owned_stock.timestamp),
        #                                 quantity = owned_stock.quantity
        #                                 # fee = owned_stock.fee
        #                             )
        #         else:
        #             pass
        return data, 200
