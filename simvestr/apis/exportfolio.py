# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 01:08:54 2020
@author: Kovid
"""

from pathlib import Path
from flask_restx import Resource, Namespace
from flask import after_this_request, send_from_directory, make_response
from simvestr.helpers.auth import requires_auth, get_user
from simvestr.helpers.portfolio import portfolio_value, get_portfolio
from simvestr.helpers.exportfolio import create_csv


api = Namespace(
    "exportfolio",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="Additional Feature - Export portfolio",
    title="Simvestr",
    description="Back-end API for exporting portfolio to csv file",
)


@api.route("")
class ExportPortfolio(Resource):
    @api.response(200, "Successful")
    @requires_auth
    def get(self):
        user = get_user()  # get user details from token
        portfolio_details = get_portfolio(user, "moving")
        portfolio_value_user = portfolio_value(user)

        file_basename = f'{portfolio_details["name"]}.xlsx'
        curr_dir = Path.cwd()
        file_path = curr_dir / "resources"
        create_csv(
            file_path, file_basename, user, portfolio_details, portfolio_value_user
        )

        @after_this_request
        def download_file(response):
            response = make_response(send_from_directory(directory=file_path, filename=file_basename, as_attachment=True))
            response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
            response.headers['export'] = 'portfolio'
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            response.headers['Cache-Control'] = 'public, max-age=0'
            return response

        return (
            {"message": "Portfolio downloaded", },
            200,
        )
