# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace
from werkzeug.security import generate_password_hash

from simvestr.models import User, Portfolio, PortfolioPrice
from simvestr.models import db
from simvestr.helpers.simvestr_email import send_email
from simvestr.helpers.db import make_salt

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

def new_user(email_id: str, first_name: str, last_name: str, role: str, password: str):
    salt = make_salt()
    password = "".join([generate_password_hash(password, method="sha256"), salt])
    new_user = User(
        email_id=email_id,
        first_name=first_name,
        last_name=last_name,
        role=role,
        password=password,
        salt=salt
    )
    db.session.add(new_user)
    db.session.commit()

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
        user = User.query.filter_by(email_id=email_id).first()
        if user:
            return (
                {"error": True, "message": "User already exists"},
                444,
            )

        if len(password) < 8:
            return (
                {"error": True, "message": "Password should be at least 8 characters", },
                447,
            )
        new_user = User(
            email_id=email_id,
            first_name=fname,
            last_name=lname,
            role="user",
            password="".join([generate_password_hash(password, method="sha256"),]),
        )
        db.session.add(new_user)
        db.session.commit()

        new_portfolio = Portfolio(
            portfolio_name=fname + '\'s Portfolio'  # make a portfolio for new user
        )
        new_user.portfolio = new_portfolio
        db.session.add(new_portfolio)
        db.session.commit()

        new_portfolioprice = PortfolioPrice(
            portfolio_id=new_user.portfolio.id,
            close_balance=100000  # give dummy amount of 100k to new user. Value should be imported from a config file.
        )
        new_user.portfolio.portfolioprice.append(new_portfolioprice)
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
