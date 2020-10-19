# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 11:57:41 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace
from werkzeug.security import generate_password_hash

from simvestr_email import send_email

# from simvestr import create_app
from ..models import User
from simvestr.models import db

api = Namespace(
    "changedetails",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="Account Settings",
    title="Simvestr",
    description="Back-end API for changing user details - Name and Password",
)

# ------------ Change user details ----------- #
changedetails_model = api.model(
    "changedetails",
    {
        "user_id": fields.Integer,
        "first_name": fields.String,
        "last_name": fields.String,
        "password": fields.String
    },
)
changedetails_parser = reqparse.RequestParser()
changedetails_parser.add_argument("user_id", type=int)
changedetails_parser.add_argument("first_name", type=str)
changedetails_parser.add_argument("last_name", type=str)
changedetails_parser.add_argument("password", type=str)

@api.route("")
class ChangeDetails(Resource):
    @api.response(200, "Successful")
    @api.response(447, "Password should be at least 8 characters")
    @api.doc(model="changedetails", body=changedetails_model, description="Resets user details")
    @api.expect(changedetails_parser, validate=True)
    def put(self):
        args = changedetails_parser.parse_args()
        user_id = args.get("user_id")
        first_name = args.get("first_name")
        last_name = args.get("last_name")
        password = args.get("password")
        user = User.query.filter_by(id = user_id).first()

        if len(password) < 8:
            return (
                {"error": True, "message": "Password should be at least 8 characters",},
                447,
            )

        user.first_name = first_name
        user.last_name = last_name
        user.password = generate_password_hash(password, method="sha256")
        db.session.commit()

        message_content = "You have succesfully changed your user details. Let us know if this wasn\'t you."
        send_email(
            user.email_id, "User details have been changed", message_content
        )  # sends a confirmation email to the user
        return (
            {"error": False, "message": "User details changed!"}, 
            200
        )
# ------------ Change user details ----------- #