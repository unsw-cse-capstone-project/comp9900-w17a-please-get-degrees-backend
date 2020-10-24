# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 12:07:31 2020

@author: Kovid
"""

# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbF9pZCI6Imsuc2Nocm9kZXItdHVybmVyQHN0dWRlbnQudW5zdy5lZHUuYXUiLCJleHAiOjE2MDM2MDkzODh9.40_crwz6fdnYEZsWN5XfSJqybHRFQVeSurfOUYt3Fh4

import numpy as np
from flask_restx import abort, reqparse
from functools import wraps
import datetime
import jwt

SECRET_KEY = "thisismysecretkeydonotstealit"
EXPIRES_IN = 86400  # 24 Hours

token_parser = reqparse.RequestParser()
token_parser.add_argument('token', location='cookies')

# def validate_passed_token(cookie):
#     try:
#         decoded_token_email_id = auth.validate_token(cookie)
#     except Exception as e:
#         return False, e
#     return True, decoded_token_email_id

class AuthenticationToken:
    SECRET_KEY = "thisismysecretkeydonotstealit"
    EXPIRES_IN = 86400  # 24 Hours

    def __init__(self, secret_key=None, expires_in=None):
        if secret_key:
            self.secret_key = secret_key
        else:
            self.secret_key = AuthenticationToken.SECRET_KEY

        if expires_in:
            self.expires_in = expires_in
        else:
            self.expires_in = AuthenticationToken.EXPIRES_IN

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

    def validate_passed_token(self, token):
        try:
            decoded_token_email_id = self.validate_token(token)
        except Exception as e:
            return False, e
        return True, decoded_token_email_id


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        arg = token_parser.parse_args()  # From http cookies
        token = arg.get("token")
        try:
            user = auth.validate_token(token)
        except Exception as e:
            abort(401, e)
        return f(*args, **kwargs)

    return decorated


def get_email():
    arg = token_parser.parse_args()  # From http cookies
    token = arg.get("token")
    passed, param = auth.validate_passed_token(token)
    if passed:
        return param
    return False

auth = AuthenticationToken(SECRET_KEY, EXPIRES_IN)