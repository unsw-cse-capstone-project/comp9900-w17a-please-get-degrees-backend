# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 20:58:41 2020
@author: Kovid
"""

from flask_restx import Resource, Namespace

from simvestr.helpers.auth import get_user
from simvestr.helpers.portfolio import all_stocks_balance

api = Namespace(
    "view stocks",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="Buying and selling stocks",
    title="Simvestr",
    description="Demo api for querying owned stocks",
)


@api.route('/')
class StocksOwnedQuery(Resource):
    def get(self, ):
        user = get_user()

        # return only stocks greater than zero

        return all_stocks_balance(user), 200
