# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""

from flask import jsonify
from flask_restx import Resource, fields, reqparse, Namespace
from werkzeug.security import generate_password_hash

# from simvestr_email import send_email
# from simvestr import create_app
from ..models import User
from simvestr.models import db

api = Namespace(
    'Signup',
    authorizations = {'TOKEN-BASED': {'name': 'API-TOKEN', 'in': 'header', 'type': 'apiKey'}},
    security = 'TOKEN-BASED',
    default = 'User Login and Authentication',
    title = 'Simvestr',
    description = 'Back-end API User signup and authentication'
)

# ---------------- Signup new user ----------- #
signup_model = api.model('signup', {
    'username': fields.String,
    'email_id': fields.String,
    'password': fields.String,
    'first_name':fields.String,
    'last_name':fields.String
})
signup_parser = reqparse.RequestParser()
signup_parser.add_argument('username', type=str)
signup_parser.add_argument('email_id', type=str)
signup_parser.add_argument('password', type=str)
signup_parser.add_argument('first_name', type=str)
signup_parser.add_argument('last_name', type=str)
@api.route('/')
class Signup(Resource):
    @api.response(200, 'Successful')
    @api.response(444, 'User already exists')
    @api.response(445, 'Email ID already exists')
    @api.doc(description="Creates a new user")
    @api.expect(signup_parser, validate=True)
    def put(self):
        args = signup_parser.parse_args()
        username = args.get('username')
        email = args.get('email_id')
        password = args.get('password')
        fname=args.get('first_name')
        lname=args.get('last_name')
        user = User.query.filter_by(username=username).first()
        email_check = User.query.filter_by(email_id=email).first()
        print("User",user)
        print("Email",email)
        if user:
              return {'message': 'User already exists'}, 444
        if email_check:
              return {'message': 'Email ID already exists'}, 445
        new_user = User(username=username, email_id=email, first_name=fname, last_name=lname, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        message_content = 'A new user from your email ID has signed-up for our free investing simlutor. Please login to start investing'
        # send_email(username, 'User created successfully', message_content) #sends a confirmation email to the user
        return jsonify({'message' : 'New user created!'})
# ---------------- Signup new user ----------- #
