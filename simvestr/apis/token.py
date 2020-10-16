# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace
from werkzeug.security import check_password_hash
import jwt
import datetime

from simvestr_email import send_email
# from simvestr import create_app
from ..models import User


api = Namespace(
    'authentication',
    security = 'TOKEN-BASED',
    default = 'User Login and Authentication',
    title = 'Simvestr',
    description = 'Back-end API User signup and authentication'
)


class AuthenticationToken:
    def __init__(self, secret_key, expires_in):
        self.secret_key = secret_key
        self.expires_in = expires_in
        
    def generate_token(self, email_id):
        info = {
            'email_id': email_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expires_in)
        }
        token_value=jwt.encode(info, self.secret_key)
        return token_value.decode('utf-8')
     
    def validate_token(self, token):
         info = jwt.decode(token, self.secret_key)
         return info['email_id']

secret_key = 'thisismysecretkeydonotstealit'
expires_in = 86400  #24 Hours
auth = AuthenticationToken(secret_key, expires_in)

# ---------------- Create Token -------------- #
credential_model = api.model(
    'Credential', 
    {
        'email_id': fields.String,
        'password': fields.String
    }
)
credential_parser = reqparse.RequestParser()
credential_parser.add_argument('email_id', type=str)
credential_parser.add_argument('password', type=str)
@api.route("")
class Token(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Unsuccessful')
    @api.response(449, 'User does not exist')
    @api.response(442, 'Incorrect password, retry')
    @api.doc(model="Credential", description="Generates a authentication token")
    @api.expect(credential_parser, validate=True)
    def get(self):
        args = credential_parser.parse_args()
        email_id = args.get('email_id')
        password = args.get('password')
        user = User.query.filter_by(email_id=email_id).first()            
        if not user:
            return (
                {'error': 'User doesn\'t exist'}, 
                449,
            )
        if not check_password_hash(user.password,password):
            return (
                {"error": True, "message" : "Incorrect password, retry"}, 
                442,
            )
        else:
            message_content = 'You have logged into Simvestr. Login will expire after 24hours!'
            send_email(user.email_id, 'Log in successful', message_content) #sends a logged in email to the user
            return (
                {"error": False, "token": auth.generate_token(user.email_id)}, 
                200,
            )
        return (
            {"error": True, "message": "authorization has been refused for those credentials."}, 
            401,
        )
# ---------------- Create Token -------------- #
