# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 21:27:58 2020

@author: Kovid
"""

from flask_restx import Resource, Namespace
from flask import after_this_request

api = Namespace(
    "logout",
    security="TOKEN-BASED",
    default="User Login and Authentication",
    title="Simvestr",
    description="Deletes the cookie from browser",
)


@api.route("")
class Token(Resource):
    @api.response(200, "Successful")
    def get(self):
        @after_this_request
        def set_cookie_value(response):
            response.delete_cookie("token")
            return response

        return 200
