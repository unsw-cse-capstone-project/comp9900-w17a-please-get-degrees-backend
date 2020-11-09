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

changenames_model = api.model(
    "ChangeNames",
    {
        "first_name": fields.String(
            required=True,
            description="User first name",
            example="Brett"    
        ),
        "last_name": fields.String(
            required=True,
            description="User last name",
            example="Lee" 
        )
    },
)
changenames_parser = reqparse.RequestParser()
changenames_parser.add_argument("first_name", type=str)
changenames_parser.add_argument("last_name", type=str)

changepwd_model = api.model(
    "ChangePwd",
    {
        "password": fields.String(
            required=True,
            description="User password",
            example="pass1234"
        )
    },
)
changepwd_parser = reqparse.RequestParser()
changepwd_parser.add_argument("password", type=str)


@api.route('/changenames')
class ChangeNames(Resource):
    @api.response(200, "Successful")
    @api.doc(model="ChangeNames", body=changenames_model, description="Resets user\'s names")
    @api.expect(changenames_parser, validate=True)
    @requires_auth
    def put(self):
        args = changenames_parser.parse_args()
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
    @api.response(448, "Password cannot contain spaces")
    @api.doc(model="ChangePwd", body=changepwd_model, description="Resets password")
    @api.expect(changepwd_parser, validate=True)
    @requires_auth
    def put(self):
        args = changepwd_parser.parse_args()
        password = args.get("password")

        user = get_user()
            
        if len(password) < 8:
            return (
                {"error": True, "message": "Password should be at least 8 characters", },
                447,
            )
        
        if " " in password:
            return (
                {"error": True, "message": "Password cannot contain spaces", },
                448,
            )
        
        change_password(user, password)
        
        message_content = "You have succesfully changed your password. Let us know if this wasn\'t you."
        # sends a confirmation email to the user
        send_email(
            user.email_id, "User details have been changed", message_content
        )  
        return (
            {"error": False, "message": "Password changed!"},
            200
        )
