# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 20:58:41 2020
@author: Kovid
"""

from flask_restx import Resource, Namespace, abort

from simvestr.models import User, Watchlist, Stock, Transaction, db
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

        stocks = user.portfolio.transactions.with_entities(
                        db.func.sum(Transaction.quantity).label("balance"),
                        Transaction.symbol
                    ).group_by("symbol").all()
        stocks = {n: q for (q, n) in stocks if q > 0} #return only stocks greater than zero

        return stocks, 200
