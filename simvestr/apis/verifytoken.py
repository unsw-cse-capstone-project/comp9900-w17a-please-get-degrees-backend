# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 11:13:21 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace, abort
from flask import Flask, request, make_response
from functools import wraps
from http import cookies
# import urllib
# import httplib2
import urllib.request as urllib
import jwt
import datetime

from ..models import User


api = Namespace(
    "verify token",
    security="TOKEN-BASED",
    default="User Login and Authentication",
    title="Simvestr",
    description="Back-end API for verifying token, authenticating user",
)


class AuthenticationToken:
    def __init__(self, secret_key, expires_in):
        self.secret_key = secret_key
        self.expires_in = expires_in

    def generate_token(self, email_id):
        info = {
            "email_id": email_id,
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(seconds=self.expires_in),
        }
        token_value = jwt.encode(info, self.secret_key)
        return token_value.decode("utf-8")

    def validate_token(self, token):
        info = jwt.decode(token, self.secret_key)
        return info["email_id"]


secret_key = "thisismysecretkeydonotstealit"
expires_in = 86400  # 24 Hours
auth = AuthenticationToken(secret_key, expires_in)


token_parser = reqparse.RequestParser()
token_parser.add_argument('token', location='cookies')

# ------------- Validate Token --------------- #

def validate_passed_token(cookie):
    try:
        decoded_token_email_id = auth.validate_token(cookie)
    except Exception as e:
        return False, e
    return True, decoded_token_email_id

# ------------- Validate Token --------------- #


@api.route("")
class SetCookie(Resource):
    @api.response(200, "Successful")
    @api.response(401, "Unsuccessful")
    # @requires_valid_token

    def get(self):
        args = token_parser.parse_args() # From http cookies
        token = args.get("token")
        # token = request.headers.get('API-TOKEN')
        passed, param =  validate_passed_token(token)
        
        if passed:
            user = User.query.filter_by(email_id = param).first()

            return (
                {"error" : False, 
                 "first_name" : user.first_name,
                 "last_name" : user.last_name,
                 "email_id" : user.email_id,
                 "message": "Authenticated with cookie set in browser"},
                200,
            )
        
        return (
            {
                "error": True,
                "message": param,
            },
            401,
        )