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
#         "user_id": fields.Integer,
        "email_id": fields.String,
        "first_name": fields.String,
        "last_name": fields.String
    },
)
changenames_parser = reqparse.RequestParser()
# changenames_parser.add_argument("user_id", type=int)
changenames_parser.add_argument("email_id", type=str)
changenames_parser.add_argument("first_name", type=str)
changenames_parser.add_argument("last_name", type=str)


changepwd_model = api.model(
    "ChangePwd",
    {
#         "user_id": fields.Integer,
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
    def put(self):
        args = changenames_parser.parse_args()
#         user_id = args.get("user_id")
        email_id = args.get("email_id")
        first_name = args.get("first_name")
        last_name = args.get("last_name")
        
#         user = User.query.filter_by(id = user_id).first()
        user = User.query.filter_by(email_id = email_id).first()

        user.first_name = first_name
        user.last_name = last_name
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
    def put(self):
        args = changepwd_parser.parse_args()
#         user_id = args.get("user_id")
        email_id = args.get("email_id")
        password = args.get("password")
        
#         user = User.query.filter_by(id = user_id).first()
        user = User.query.filter_by(email_id = email_id).first()

        if len(password) < 8:
            return (
                {"error": True, "message": "Password should be at least 8 characters",},
                447,
            )

        user.password = generate_password_hash(password, method="sha256")
        db.session.commit()

        message_content = "You have succesfully changed your password. Let us know if this wasn\'t you."
        send_email(
            user.email_id, "User details have been changed", message_content
        )  # sends a confirmation email to the user
        return (
            {"error": False, "message": "Password changed!"}, 
            200
        )
# ------------ Change user details ----------- #
