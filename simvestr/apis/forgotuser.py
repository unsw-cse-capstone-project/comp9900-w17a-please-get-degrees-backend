# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace
from flask import jsonify
from werkzeug.security import generate_password_hash

from simvestr_email import send_email
# from simvestr import create_app
from ..models import User
import random
from .. import db

api = Namespace(
    'Forgot User',
    security = 'TOKEN-BASED',
    default = 'User Login and Authentication',
    title = 'Simvestr',
    description = 'Back-end API User signup and authentication'
)


# ---------------- Forgot User --------------- #
forgotuser_model = api.model('forgotuser', {
    'username': fields.String,
    'password': fields.String,
    'OTP':fields.String
})
forgotuser_parser = reqparse.RequestParser()
forgotuser_parser.add_argument('username', type=str)
forgotuser_parser.add_argument('password', type=str)
forgotuser_parser.add_argument('OTP', type=str)

forgotuser_email_model = api.model('forgotuser', {
    'username': fields.String,
})
forgotuser_email_parser = reqparse.RequestParser()
forgotuser_email_parser.add_argument('username', type=str)

    
random_OTP = random.randint(1000,9999)
email_sent_flag = False
@api.route('/')
class ForgotUser(Resource):
    @api.response(200, 'Successful')
    @api.response(445, 'Bad OTP')
    @api.doc(description="Resets password for user using OTP")
    @api.expect(forgotuser_email_parser, validate=True)
    def get(self):
        args = forgotuser_email_parser.parse_args()
        username = args.get('username')
        print('\nusername to send email:', username) #z5240067
        user = User.query.filter_by(username=username).first()
        global random_OTP
        message_content = f'ALERT! You have requested password change for your Simvestr account. Please copy the 4 digit OTP {random_OTP}.'
        send_email(user.email_id, f'Forgot Password - OTP: {random_OTP}', message_content) #sends a confirmation email to the user
        return jsonify({'message' : 'Email sent!'})
    
    @api.expect(forgotuser_parser, validate=True)
    def put(self):
        args = forgotuser_parser.parse_args()
        username = args.get('username')
        password = args.get('password')
        one_time_pass = args.get('OTP')
        user = User.query.filter_by(email=username).first()
        print('\nusername:', username) #z5240067
        print('password', password)
        print('one_time_pass:',one_time_pass)
        print("user:",user,'\n')
        global random_OTP
        # global email_sent_flag
        # if not email_sent_flag:
        #     message_content = f'ALERT! You have requested password change for your Simvestr account. Please copy the 4 digit OTP {random_OTP}.'
        #     send_email(username, f'Forgot Password - OTP: {random_OTP}', message_content) #sends a confirmation email to the user
        #     email_sent_flag = True
        #     return jsonify({'message' : 'Email sent!'})  
        if one_time_pass != str(random_OTP):
              return {'message': 'The OTP you entered is incorrect!'}, 445
        user.password = generate_password_hash(password, method='sha256')
        db.session.commit()
        message_content = 'ALERT! Your password for Simvestr has been changed. Please contact us if this wasn\'t you.'
        send_email(user.email_id, 'Password updated successfully', message_content) #sends a confirmation email to the user
        return jsonify({'message' : 'Password updated!'})
# ---------------- Forgot User --------------- #