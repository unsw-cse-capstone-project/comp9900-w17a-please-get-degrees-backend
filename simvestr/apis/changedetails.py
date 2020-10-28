# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 11:57:41 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace

from simvestr.helpers.auth import get_user, requires_auth
from simvestr.helpers.simvestr_email import send_email
from simvestr.helpers.user import change_password
from simvestr.models import Portfolio
from simvestr.models import db

api = Namespace(
    "change user details",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="Account Settings",
    title="Simvestr",
    description="Back-end API for changing user details - Name and Password",
)

# ------------ Change user details ----------- #
changenames_model = api.model(
    "ChangeNames",
    {
        "email_id": fields.String,
        "first_name": fields.String,
        "last_name": fields.String
    },
)
changenames_parser = reqparse.RequestParser()
changenames_parser.add_argument("email_id", type=str)
changenames_parser.add_argument("first_name", type=str)
changenames_parser.add_argument("last_name", type=str)

changepwd_model = api.model(
    "ChangePwd",
    {
        "email_id": fields.String,
        "password": fields.String
    },
)
changepwd_parser = reqparse.RequestParser()
changepwd_parser.add_argument("email_id", type=str)
changepwd_parser.add_argument("password", type=str)


@api.route('/changenames')
class ChangeNames(Resource):
    @api.response(200, "Successful")
    @api.doc(model="ChangeNames", body=changenames_model, description="Resets user\'s names")
    @api.expect(changenames_parser, validate=True)
    @requires_auth
    def put(self):
        args = changenames_parser.parse_args()
        email_id = args.get("email_id")
        first_name = args.get("first_name")
        last_name = args.get("last_name")

        user = get_user()

        user.first_name = first_name
        user.last_name = last_name
        db.session.commit()

        # if name is changed, change portfolio name as well
        portfolio = Portfolio.query.filter_by(id=user.id).first()
        portfolio.portfolio_name = user.first_name + '\'s Portfolio'
        db.session.commit()

        message_content = "You have succesfully changed your personal details. Let us know if this wasn\'t you."
        send_email(
            user.email_id, "User details have been changed", message_content
        )  # sends a confirmation email to the user
        return (
            {"error": False, "message": "User details changed!"},
            200
        )


@api.route('/changepwd')
class ChangePwd(Resource):
    @api.response(200, "Successful")
    @api.response(447, "Password should be at least 8 characters")
    @api.doc(model="ChangePwd", body=changepwd_model, description="Resets password")
    @api.expect(changepwd_parser, validate=True)
    @requires_auth
    def put(self):
        args = changepwd_parser.parse_args()
        password = args.get("password")

        user = get_user()

        # Need to add check for invalid characters
        if len(password) < 8:
            return (
                {"error": True, "message": "Password should be at least 8 characters", },
                447,
            )
        change_password(user, password)

        message_content = "You have succesfully changed your password. Let us know if this wasn\'t you."
        send_email(
            user.email_id, "User details have been changed", message_content
        )  # sends a confirmation email to the user
        return (
            {"error": False, "message": "Password changed!"},
            200
        )
# ------------ Change user details ----------- #
