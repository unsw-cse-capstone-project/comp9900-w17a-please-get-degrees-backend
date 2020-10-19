# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace
from werkzeug.security import generate_password_hash

from simvestr_email import send_email

# from simvestr import create_app
from ..models import User, Portfolio, PortfolioPrice
from simvestr.models import db

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

# ---------------- Signup new user ----------- #
signup_model = api.model(
    "Signup",
    {
        "email_id": fields.String,
        "password": fields.String,
        "first_name": fields.String,
        "last_name": fields.String,
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
    @api.response(444, "User already exists")
    @api.response(445, "Email ID already exists")
    @api.response(446, "Username should be at least 8 characters")
    @api.response(447, "Password should be at least 8 characters")
    @api.doc(model="Signup", body=signup_model, description="Creates a new user")
    def post(self):
        args = signup_parser.parse_args()
        email_id = args.get("email_id")
        password = args.get("password")
        fname = args.get("first_name")
        lname = args.get("last_name")
        user = User.query.filter_by(email_id = email_id).first()
        if user:
            return (
                {"error": True, "message": "User already exists"}, 
                444,
            )

        if len(password) < 8:
            return (
                {"error": True, "message": "Password should be at least 8 characters",},
                447,
            )
        new_user = User(
            email_id = email_id,
            first_name = fname,
            last_name = lname,
            role = "user",
            password = generate_password_hash(password, method="sha256"),
        )
        db.session.add(new_user)
        db.session.commit()
        
        user = User.query.filter_by(email_id = email_id).first()
        new_portfolio = Portfolio(
            user_id = user.id,
            portfolio_name = fname + '\'s Portfolio' # make a portfolio for new user
        )
        db.session.add(new_portfolio)
        db.session.commit()
        
        port = Portfolio.query.filter_by(user_id = user.id).first()
        new_portfolioprice = PortfolioPrice(
            user_id = user.id,
            portfolio_id = port.id,
            close_balance = 100000 # give dummy amount of 100k to new user
        )
        db.session.add(new_portfolioprice)
        db.session.commit()
        
        message_content = "A new user from your email ID has signed-up for our free investing simulator. Please login to start investing"
        send_email(
            email_id, "User created successfully", message_content
        )  # sends a confirmation email to the user
        return (
            {"error": False, "message": "New user created!"}, 
            200
        )
# ---------------- Signup new user ----------- #