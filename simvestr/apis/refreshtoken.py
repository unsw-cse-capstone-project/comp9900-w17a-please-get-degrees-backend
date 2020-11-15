# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 14:20:41 2020
@author: Kovid
"""

from flask_restx import Resource, reqparse, Namespace
from flask import after_this_request


from simvestr.models import User
from simvestr.helpers.simvestr_email import send_email
from simvestr.helpers.auth import auth, get_user, requires_auth
from simvestr.models.api_models import login_model

api = Namespace(
    "refresh token",
    security="TOKEN-BASED",
    default="User Login and Authentication",
    title="Simvestr",
    description="Resets token cookie in browser",
)


@api.route("")
class Token(Resource):
    @api.response(200, "Successful")
    @api.doc(
        descriptions="Resets token cookie in browser"
    )
    def put(self):
        user = get_user()

        # set cookie in browser
        token = auth.generate_token(user.email_id)

        @after_this_request
        def set_cookie_value(response):
            response.set_cookie("token", value=token, httponly=True)
            return response

        return 200
