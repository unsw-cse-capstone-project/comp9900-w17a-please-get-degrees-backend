# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 11:13:21 2020

@author: Kovid
"""

from flask_restx import Resource, reqparse, Namespace
import jwt
import datetime

from simvestr.models import User
from simvestr.helpers.auth import auth


api = Namespace(
    "verify token",
    security="TOKEN-BASED",
    default="User Login and Authentication",
    title="Simvestr",
    description="Back-end API for verifying token, authenticating user",
)



secret_key = "thisismysecretkeydonotstealit"
expires_in = 86400  # 24 Hours
# auth = AuthenticationToken(secret_key, expires_in)


token_parser = reqparse.RequestParser()
token_parser.add_argument('token', location='cookies')

# ------------- Validate Token --------------- #



# ------------- Validate Token --------------- #


@api.route("")
class VerifyToken(Resource):
    @api.response(200, "Successful")
    @api.response(401, "Unsuccessful")
    def get(self):
        args = token_parser.parse_args() # From http cookies
        token = args.get("token")
        if token == None:
            return (
            {
                "error": True,
                "message": "Cookie token not found, login again",
            },
            405,
            )
        passed, param =  auth.validate_passed_token(token)
        
        if passed:
            user = User.query.filter_by(email_id = param).first()

            return (
                {"first_name" : user.first_name,
                 "last_name" : user.last_name,
                 "email_id" : user.email_id,
                 "message": "Authenticated with cookie set in browser"},
                200,
            )
        
        return (
            {
                "message": param,
            },
            401,
        )
