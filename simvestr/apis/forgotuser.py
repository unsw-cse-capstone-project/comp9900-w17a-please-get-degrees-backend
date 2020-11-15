# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""
import random

from flask_restx import Resource, reqparse, Namespace, abort
from werkzeug.security import generate_password_hash

from simvestr.models import db, User
from simvestr.helpers.simvestr_email import send_email
from simvestr.models.api_models import forgotuser_model, forgotuser_email_model

api = Namespace(
    'forgot user password',
    security='TOKEN-BASED',
    default='User Login and Authentication',
    title='Simvestr',
    description='Back-end API User signup and authentication'
)

api.models[forgotuser_model.name] = forgotuser_model
api.models[forgotuser_email_model.name] = forgotuser_email_model

forgotuser_parser = reqparse.RequestParser()
forgotuser_parser.add_argument('email_id', type=str)
forgotuser_parser.add_argument('password', type=str)
forgotuser_parser.add_argument('OTP', type=str)

forgotuser_email_parser = reqparse.RequestParser()
forgotuser_email_parser.add_argument('email_id', type=str)

random_OTP = 1234


@api.route("")
class ForgotUser(Resource):
    @api.response(200, 'Successful')
    @api.response(404, "User not found")
    @api.response(411, "Length required")
    @api.response(422, "Unprocessable entity")
    @api.doc(id="reset_user_password", model=forgotuser_email_model,
             description="Send OTP to registered email")
    @api.expect(forgotuser_email_parser, validate=True)
    def get(self):
        args = forgotuser_email_parser.parse_args()
        email_id = (args.get("email_id")).lower()
        user = User.query.filter_by(email_id=email_id).first()
        if not user:
            return abort(404, "User not found")

        global random_OTP
        random_OTP = random.randint(1000, 9999)
        print(f'\n\nOTP: {random_OTP}\n\n')
        message_content = f'ALERT! You have requested password change for your Simvestr account. Please copy the 4 digit OTP {random_OTP}.'
        # sends a confirmation email to the user
        send_email(user.email_id, f'Forgot Password - OTP: {random_OTP}', message_content)
        return 200

    @api.doc(id="reset_user_password", body=forgotuser_model,
             description="Resets password for user using OTP")
    @api.expect(forgotuser_parser, validate=True)
    def put(self):
        args = forgotuser_parser.parse_args()
        email_id = (args.get('email_id')).lower()
        password = args.get('password')
        one_time_pass = args.get('OTP')
        user = User.query.filter_by(email_id=email_id).first()
        if not user:
            return abort(404, "User not found")

        if len(password) < 8:
            return abort(411, "Password should be atleast 8 characters")

        if " " in password:
            return abort(422, "Password cannot contain spaces")

        global random_OTP

        if one_time_pass != str(random_OTP):
            return abort(422, "The OTP you entered is incorrect!")

        user.password = generate_password_hash(password, method='sha256')
        db.session.commit()

        message_content = "ALERT! Your password for Simvestr has been changed. Please contact us if this wasn\"t you."
        # sends a confirmation email to the user
        send_email(email_id, "Password updated successfully", message_content)
        return 200
