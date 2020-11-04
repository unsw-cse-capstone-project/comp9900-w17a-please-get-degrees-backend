# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 21:27:58 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace
from flask import make_response, after_this_request
from werkzeug.security import check_password_hash
import jwt
import datetime

from simvestr.models import User
from simvestr.helpers.simvestr_email import send_email
from simvestr.helpers.auth import auth

api = Namespace(
    "logout - remove cookie",
    security="TOKEN-BASED",
    default="User Login and Authentication",
    title="Simvestr",
    description="Deletes the cookie from browser",
)

@api.route("")
class Token(Resource):
    @api.response(200, "Successful")
    @api.response(401, "Unsuccessful")
    def get(self):

        @after_this_request
        def set_cookie_value(response):
            response.delete_cookie("token")
            return response

        return (
            {"message": "Logout successful"},
            200,
        )