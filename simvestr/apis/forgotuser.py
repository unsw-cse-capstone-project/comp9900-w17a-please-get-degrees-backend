# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:27:41 2020

@author: Kovid
"""
import random

from flask_restx import Resource, reqparse, Namespace
from werkzeug.security import generate_password_hash

from simvestr.models import User, db
from simvestr.helpers.simvestr_email import send_email
from simvestr.helpers.user import change_password
from simvestr.models.api_models import forgotuser_model, forgotuser_email_model

api = Namespace(
    "forgot user password",
    security = "TOKEN-BASED",
    default = "User Login and Authentication",
    title = "Simvestr",
    description = "Back-end API User signup and authentication"
)


api.models[forgotuser_model.name] = forgotuser_model
api.models[forgotuser_email_model.name] = forgotuser_email_model

forgotuser_parser = reqparse.RequestParser()
forgotuser_parser.add_argument("email", type=str)
forgotuser_parser.add_argument("password", type=str)
forgotuser_parser.add_argument("OTP", type=str)

forgotuser_email_parser = reqparse.RequestParser()
forgotuser_email_parser.add_argument("email", type=str)

random_OTP = 1234


@api.route("")
class ForgotUser(Resource):
    @api.response(200, "Successful")
    @api.response(404, "User not found")
    @api.response(411, "Length required")
    @api.response(422, "Unprocessable entity")
    @api.doc(id="reset_user_password", model="Forgot User Email", description="Send OTP to registered email")
    @api.marshal_with(forgotuser_email_model)
    @api.expect(forgotuser_email_parser, validate=True)@api.marshal_with(forgotuser_email_model)
    def get(self):
        args = forgotuser_email_parser.parse_args()
        email_id = (args.get("email")).lower()
        user = User.query.filter_by(email_id=email_id).first()
        if not user:
            return (
            {"message": "User not found"}, 
            404,
        )
        
        global random_OTP
        random_OTP = random.randint(1000,9999)
        message_content = f"ALERT! You have requested password change for your Simvestr account. Please copy the 4 digit OTP {random_OTP}."
        #sends a confirmation email to the user
        send_email(user.email_id, f"Forgot Password - OTP: {random_OTP}", message_content)
        print(f'\n\nOTP: {random_OTP}\n\n') # MAKE SURE TO TURN IT OFF BEFORE SUBMISSION
        return (
            {"message": "Email sent!"}, 
            200,
        )
    
    @api.doc(id="reset_user_password", model="Forgot User", body=forgotuser_model, description="Resets password for user using OTP")
    @api.marshal_with(forgotuser_model)
    @api.expect(forgotuser_parser, validate=True)
    def put(self):
        args = forgotuser_parser.parse_args()
        email_id = (args.get("email")).lower()
        password = args.get("password")
        one_time_pass = args.get("OTP")
        user = User.query.filter_by(email_id=email_id).first()
        if not user:
            return (
                {"message": "User not found"}, 
            404,
            )
        
        if len(password) < 8:
            return (
                {"message": "Password should be atleast 8 characters"}, 
                411,
            )
        
        if " " in password:
            return (
                {"message": "Password cannot contain spaces", },
                422,
            )
        
        global random_OTP
        
        if one_time_pass != str(random_OTP):
            return (
                {"message": "The OTP you entered is incorrect!"}, 
                422,
            )

        change_password(user, password)
        
        message_content = "ALERT! Your password for Simvestr has been changed. Please contact us if this wasn\"t you."
        #sends a confirmation email to the user
        send_email(email_id, "Password updated successfully", message_content) 
        return (
            {"message": "Password updated!"}, 
            200
        )
