# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""

from flask_restx import Resource, reqparse, Namespace
from flask import after_this_request

from simvestr.models import User
from simvestr.helpers.simvestr_email import send_email
from simvestr.helpers.auth import auth, check_password
from simvestr.models.api_models import login_model

api = Namespace(
    "login",
    security="TOKEN-BASED",
    default="User Login and Authentication",
    title="Simvestr",
    description="Generates a JWT, sets a cookie in browser",
)

api.models[login_model.name] = login_model

login_parser = reqparse.RequestParser()
login_parser.add_argument("email", type=str)
login_parser.add_argument("password", type=str)


@api.route("")
class Token(Resource):
    @api.response(200, "Successful")
    @api.response(401, "Incorrect password, retry")
    @api.response(404, "User not found")
    @api.doc(
        id="login_user", 
        body=login_model, 
        descriptions="Generates an authentication token"
    )
    def post(self):
        args = login_parser.parse_args()
        email_id = (args.get("email")).lower()
        password = args.get("password")
        user = User.query.filter_by(email_id=email_id).first()
        if not user:
            return (
                {"message": "User not found"},
                404,
            )
        if not check_password(user, password):
            return (
                {"message": "Incorrect password, retry"},
                401,
            )

        message_content = (
            "You have logged into Simvestr. Login will expire after 24 hours!"
        )

        # sends a logged in email to the user
        send_email(
            user.email_id, "Log in successful", message_content
        )

        # set cookie in browser
        token = auth.generate_token(user.email_id)

        @after_this_request
        def set_cookie_value(response):
            response.set_cookie("token", value=token, httponly=True)
            return response

        return 200
