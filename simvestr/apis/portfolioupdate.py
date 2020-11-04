# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 01:08:54 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace

from simvestr.helpers.auth import requires_auth, get_user
from simvestr.helpers.portfolio import stock_balance
from simvestr.models import db, Transaction
from simvestr.apis.search import StockDetails
from simvestr.apis.portfolio import PortfolioQuery
from simvestr.helpers.portfolio import calculate_all_portfolios_values

import requests
import csv

api = Namespace(
    "update portfolios",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="Additional Feature - Export portfolio",
    title="Simvestr",
    description="Back-end API for exporting portfolio to csv file",
)


@api.route("")
class UpdatePortfolio(Resource):
    @api.response(200, "Successful")
    @requires_auth
    def get(self):

        calculate_all_portfolios_values()
        print('Portfolio updated')
        
        return (
            {
                "message": "Portfolios updated",
            },
            200,
        )