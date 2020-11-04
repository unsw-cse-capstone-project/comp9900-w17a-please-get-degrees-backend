# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 12:07:31 2020

@author: Kovid
"""


import numpy as np

from functools import wraps
import datetime
import jwt

from flask_restx import abort, reqparse

from simvestr.models import User

SECRET_KEY = "thisismysecretkeydonotstealit"
EXPIRES_IN = 86400  # 24 Hours

token_parser = reqparse.RequestParser()
token_parser.add_argument('token', location='cookies')


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


def get_user():
    try:
        email = get_email()
    except Exception as e:
        abort(401, e)

    user = User.query.filter_by(email_id=email).first()
    if not user:
        abort(449, "User doesn't exist")

    return user


auth = AuthenticationToken(SECRET_KEY, EXPIRES_IN)
