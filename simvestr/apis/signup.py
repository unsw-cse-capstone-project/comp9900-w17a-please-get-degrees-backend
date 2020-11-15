# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""

from flask_restx import Resource, reqparse, Namespace

from simvestr.helpers.simvestr_email import send_email
from simvestr.helpers.user import create_new_user
from simvestr.models import User
from simvestr.models.api_models import signup_model

api = Namespace(
    "signup",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="User Login and Authentication",
    title="Simvestr",
    description="Back-end API for new user signup",
)

api.models[signup_model.name] = signup_model

signup_parser = reqparse.RequestParser()
signup_parser.add_argument("email", type=str)
signup_parser.add_argument("password", type=str)
signup_parser.add_argument("first_name", type=str)
signup_parser.add_argument("last_name", type=str)


@api.route("")
class Signup(Resource):
    @api.response(201, "Successful")
    @api.response(403, "Already exists")
    @api.response(411, "Length required")
    @api.response(422, "Unprocessable entity")
    @api.doc(id="create_new_user", body=signup_model, description="Creates a new user")
    def post(self):
        args = signup_parser.parse_args()
        email_id = args["email"].lower()
        password = args["password"]
        fname = args["first_name"]
        lname = args["last_name"]

        if len(email_id) < 1:
            return (
                {"message": "Email is required"},
                422,
            )

        user = User.query.filter_by(email_id=email_id).first()

        if user:
            return (
                {"message": "User already exists"},
                403,
            )

        if len(password) < 8:
            return (
                {"message": "Password should be at least 8 characters", },
                411,
            )

        if " " in password:
            return (
                {"message": "Password cannot contain spaces", },
                422,
            )

        create_new_user(
            email_id=email_id,
            first_name=fname,
            last_name=lname,
            password=password,
        )

        message_content = "A new user from your email ID has signed-up for " \
                          "our free investing simulator. Please login to start investing"
        # sends a confirmation email to the user
        send_email(
            email_id, "User created successfully", message_content
        )

        return (
            {"message": "New user created!"},
            201
        )
