# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace
from werkzeug.security import check_password_hash
import jwt
import datetime

# from simvestr_email import send_email
# from simvestr import create_app
from ..models import User


api = Namespace(
    'Authentication',
    security = 'TOKEN-BASED',
    default = 'User Login and Authentication',
    title = 'Simvestr',
    description = 'Back-end API User signup and authentication'
)


class AuthenticationToken:
    def __init__(self, secret_key, expires_in):
        self.secret_key = secret_key
        self.expires_in = expires_in
        
    def generate_token(self, username):
        info = {
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expires_in)
        }
        token_value=jwt.encode(info, self.secret_key)
        return token_value.decode('utf-8')
     
    def validate_token(self, token):
         info = jwt.decode(token, self.secret_key)
         return info['username']

secret_key = 'thisismysecretkeydonotstealit'
expires_in = 86400  #24 Hours
auth = AuthenticationToken(secret_key, expires_in)

# ---------------- Create Token -------------- #
credential_model = api.model('credential', {
    'username': fields.String,
    'password': fields.String
})
credential_parser = reqparse.RequestParser()
credential_parser.add_argument('username', type=str)
credential_parser.add_argument('password', type=str)
@api.route('/')
class Token(Resource):
    @api.response(200, 'Successful')
    @api.response(455, 'User does not exist')
    @api.response(456, 'Incorrect password, retry')
    @api.doc(description="Generates a authentication token")
    @api.expect(credential_parser, validate=True)
    def get(self):
        args = credential_parser.parse_args()
        username = args.get('username')
        password = args.get('password')
        user = User.query.filter_by(email=username).first()
        if not user  or not check_password_hash(user.password, password):
            return {'message': 'User does not exists'}, 455
        isSamePassword=check_password_hash(user.password,password)        
        if not isSamePassword:
            return {'message': 'Incorrect password, retry'}, 456
        else:
            message_content = 'You have logged into Simvestr. Login will expire after 24hours!'
            # send_email(user.email_id, 'Log in successful', message_content) #sends a logged in email to the user
            return {"token": auth.generate_token(username)}
        return {"message": "authorization has been refused for those credentials."}, 401
# ---------------- Create Token -------------- #