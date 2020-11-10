# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

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
    "login",
    security="TOKEN-BASED",
    default="User Login and Authentication",
    title="Simvestr",
    description="Generates a JWT, sets a cookie in browser",
)

credential_model = api.model(
    "Credential",
    {
        "email": fields.String(
            required=True,
            description="User email",
            example="test@test.com"
        ),
        "password": fields.String(
            required=True,
            description="User password",
            example="pass1234"
        )
    }
)
credential_parser = reqparse.RequestParser()
credential_parser.add_argument("email", type=str)
credential_parser.add_argument("password", type=str)


def validate_password(user, test_password):
    test_password = "".join([test_password, user.salt])
    return (user.password, test_password)


@api.route("")
class Token(Resource):
    @api.response(200, "Successful")
    @api.response(401, "Unsuccessful")
    @api.response(449, "User does not exist")
    @api.response(442, "Incorrect password, retry")
    @api.doc(
        model="Credential",
        body=credential_model,
        descriptions="Generates an authentication token",
    )
    def post(self):
        args = credential_parser.parse_args()
        email_id = (args.get("email")).lower()
        password = args.get("password")
        user = User.query.filter_by(email_id=email_id).first()
        if not user:
            return (
                {"message": "User doesn't exist"},
                449,
            )
        if not validate_password(user, password):
            return (
                {"message": "Incorrect password, retry"},
                442,
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

        return (
            {"message": "Login successful"},
            200,
        )
