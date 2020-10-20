# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 20:58:41 2020
@author: Kovid
"""

from flask_restx import Resource, Namespace
from ..models import User, Watchlist, Stock, Transaction


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
   

@api.route('/<int:user_id>')
class StocksOwnedQuery(Resource):
    def get(self, user_id: int):
        # stocks = [t.symbol for t in Transaction.query.with_entities(Transaction.symbol).distinct()] # all distinct symbols
        
        #get disctinct stocks from transaction for user
        stocks = Transaction.query.with_entities((Transaction.symbol).distinct())\
                .filter_by(trade_type = "settled", user_id = user_id).all()
        
        #get disctinct portfolios for user
        portfolios = Transaction.query.with_entities((Transaction.portfolio_id).distinct())\
                .filter_by(trade_type = "settled", user_id = user_id).all()
                
        stocks_list = [s[0] for s in stocks]
        portfolios_list = [p[0] for p in portfolios]
        data = {}
        for p in portfolios_list:
            for s in stocks_list:
                check_stock = Transaction.query.filter_by(
                                                           user_id = user_id, \
                                                           portfolio_id = p, \
                                                           symbol = s, \
                                                           trade_type = "settled" \
                                                         ).all()
                if check_stock:
                    owned_stock = check_stock[-1]
                    if owned_stock.quantity >= 1:
                        data[owned_stock.id] = dict(
                                        user_id = owned_stock.user_id, 
                                        portfolio_id = owned_stock.portfolio_id, 
                                        symbol = owned_stock.symbol, 
                                        cost = owned_stock.cost, 
                                        # trade_type = owned_stock.trade_type, 
                                        # timestamp = str(owned_stock.timestamp), 
                                        quantity = owned_stock.quantity 
                                        # fee = owned_stock.fee
                                    )
                else:
                    pass
        return (data)
