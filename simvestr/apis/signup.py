# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace

from simvestr.helpers.simvestr_email import send_email
from simvestr.helpers.user import create_new_user
from simvestr.models import User

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

signup_model = api.model(
    "Signup",
    {
        "email_id": fields.String(
            required=True,
            description="User email",
            example="test@gmail.com"
        ),
        "password": fields.String(
            required=True,
            description="User password",
            example="pass1234"
        ),
        "first_name": fields.String(
            required=True,
            description="User first name",
            example="Brett"    
        ),
        "last_name": fields.String(
            required=True,
            description="User last name",
            example="Lee"    
        ),
    },
)
signup_parser = reqparse.RequestParser()
signup_parser.add_argument("email_id", type=str)
signup_parser.add_argument("password", type=str)
signup_parser.add_argument("first_name", type=str)
signup_parser.add_argument("last_name", type=str)


@api.route("")
class Signup(Resource):
    @api.response(200, "Successful")
    @api.response(403, "Already exists")
    # @api.response(403, "Email ID already exists")
    @api.response(422, "Unprocessable entity")
    @api.response(448, "Password cannot contain spaces")
    # @api.response(422, "Password should be at least 8 characters")
    @api.doc(model="Signup", body=signup_model, description="Creates a new user")
    def post(self):
        args = signup_parser.parse_args()
        email_id = (args.get("email_id")).lower()
        password = args.get("password")
        fname = args.get("first_name")
        lname = args.get("last_name")

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
                422,
            )
        
        if " " in password:
            return (
                {"error": True, "message": "Password cannot contain spaces", },
                448,
            )

        create_new_user(
            email_id=email_id,
            first_name=fname,
            last_name=lname,
            password=password,
        )

        message_content = "A new user from your email ID has signed-up for our free investing simulator. Please login to start investing"
        # sends a confirmation email to the user
        send_email(
            email_id, "User created successfully", message_content
        )
        
        return (
            {"message": "New user created!"},
            200
        )
