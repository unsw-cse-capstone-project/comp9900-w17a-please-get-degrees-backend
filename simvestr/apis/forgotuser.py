# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace
from werkzeug.security import generate_password_hash

from simvestr.helpers.simvestr_email import send_email
# from simvestr import create_app
from ..models import User
import random
from simvestr.models import db

api = Namespace(
    'forgotuser',
    security = 'TOKEN-BASED',
    default = 'User Login and Authentication',
    title = 'Simvestr',
    description = 'Back-end API User signup and authentication'
)


# ---------------- Forgot User --------------- #
forgotuser_model = api.model(
    'ForgotUser', 
    {
        'email_id': fields.String,
        'password': fields.String,
        'OTP':fields.String
    }
)

forgotuser_parser = reqparse.RequestParser()
forgotuser_parser.add_argument('email_id', type=str)
forgotuser_parser.add_argument('password', type=str)
forgotuser_parser.add_argument('OTP', type=str)

forgotuser_email_model = api.model('forgotuser', {
    'email_id': fields.String,
})
forgotuser_email_parser = reqparse.RequestParser()
forgotuser_email_parser.add_argument('email_id', type=str)

random_OTP = 1234
@api.route("")
class ForgotUser(Resource):
    @api.response(200, 'Successful')
    @api.response(448, 'Bad OTP')
    @api.response(447, 'Password should be atleast 8 characters')
    @api.response(449, 'User doesn\'t exist')
    @api.doc(model="ForgotUser", description="Resets password for user using OTP")
    @api.expect(forgotuser_email_parser, validate=True)
    def get(self):
        args = forgotuser_email_parser.parse_args()
        email_id = args.get('email_id')
        user = User.query.filter_by(email_id=email_id).first()
        if not user:
            return (
            {"error": True, "message": "User doesn\'t exist"}, 
            449,
        )
        
        global random_OTP
        random_OTP = random.randint(1000,9999)
        message_content = f'ALERT! You have requested password change for your Simvestr account. Please copy the 4 digit OTP {random_OTP}.'
        send_email(user.email_id, f'Forgot Password - OTP: {random_OTP}', message_content) #sends a confirmation email to the user
        return ({"error": False, "message": "Email sent!"}, 200)
    
    @api.doc(model="ForgotUser", body=forgotuser_model, description="Resets password for user using OTP")
    @api.expect(forgotuser_parser, validate=True)
    def put(self):
        args = forgotuser_parser.parse_args()
        email_id = args.get('email_id')
        password = args.get('password')
        one_time_pass = args.get('OTP')
        user = User.query.filter_by(email_id=email_id).first()
        if not user:
            return (
                {"error": True, "message": "User doesn\'t exist"}, 
                449,
            )
        
        global random_OTP
        if len(password) < 8:
            return (
                {"error": True, "message": "Password should be atleast 8 characters"}, 
                447,
            )

        if one_time_pass != str(random_OTP):
            return (
                {"error": True, "message": "The OTP you entered is incorrect!"}, 
                448,
            )

        user.password = generate_password_hash(password, method='sha256')
        db.session.commit()
        
        message_content = 'ALERT! Your password for Simvestr has been changed. Please contact us if this wasn\'t you.'
        send_email(email_id, 'Password updated successfully', message_content) #sends a confirmation email to the user
        return (
            {"error": False, "message": "Password updated!"}, 
            200
        )
# ---------------- Forgot User --------------- #
