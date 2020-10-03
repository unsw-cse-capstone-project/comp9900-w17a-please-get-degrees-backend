import pandas as pd
import json
from flask import Flask, request,jsonify, flash, redirect
from flask_restplus import Resource, Api, fields, reqparse, abort
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user
from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
import requests


app = Flask(__name__)
api = Api(app,
          authorizations = {'TOKEN-BASED': {'name': 'API-TOKEN', 'in': 'header', 'type': 'apiKey'}},
          security = 'TOKEN-BASED',
          default = 'Stocks!',
          title = 'Simvestr',
          description = 'Back-end API for finding Stocks based on their Symbol'
         )

class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
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
app.config['SECRET_KEY']='thisismysecretkeydonotstealit'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login_db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']  = False
expires_in = 86400  #24 Hours
auth = AuthenticationToken(secret_key, expires_in)

login_db=SQLAlchemy(app)


credential_model = api.model('credential', {
    'username': fields.String,
    'password': fields.String
})

credential_parser = reqparse.RequestParser()
credential_parser.add_argument('username', type=str)
credential_parser.add_argument('password', type=str)

signup_model = api.model('signup', {
    'username': fields.String,
    'password': fields.String,
    'name':fields.String
})

signup_parser = reqparse.RequestParser()
signup_parser.add_argument('username', type=str)
signup_parser.add_argument('password', type=str)
signup_parser.add_argument('name', type=str)


class User(UserMixin, login_db.Model):
    id = login_db.Column(login_db.Integer, primary_key=True)
    email = login_db.Column(login_db.String(100), unique=True)
    password = login_db.Column(login_db.String(100))
    name = login_db.Column(login_db.String(1000))
    
    
# If table doesn't exist, create table
engine = create_engine("sqlite:///login_db.sqlite3")  # Access the DB Engine
if not engine.dialect.has_table(engine, 'user'):  # If table don't exist, Create.
    metadata = MetaData(engine)
    # Create a table with the appropriate Columns
    Table('user', metadata,
          Column('id', Integer, primary_key=True, nullable=False), 
          Column('email', String), Column('password', String),
          Column('name', String))
    # Implement the creation
    metadata.create_all()
    
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('API-TOKEN')
        try:
            user=auth.validate_token(token)
        except Exception as e:
            abort(401, e)
        return f(*args, **kwargs)
    return decorated

parser = reqparse.RequestParser()

@api.route('/token')
class Token(Resource):
    @api.response(200, 'Successful')
    @api.response(455, 'User does not exists or password is incorrect')
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
        if isSamePassword:
            return {"token": auth.generate_token(username)}
        return {"message": "authorization has been refused for those credentials."}, 401


@api.route('/signup')
class Signup(Resource):
    @api.response(200, 'Successful')
    @api.response(444, 'User already exists')
    @api.doc(description="creates user")
    @api.expect(signup_parser, validate=True)
    def put(self):
        args = signup_parser.parse_args()
        username = args.get('username')
        password = args.get('password')
        name=args.get('name')
        user = User.query.filter_by(email=username).first()
        print("User",user)
        if user:
              return {'message': 'User exists'}, 444
        new_user = User(email=username, name=name, password=generate_password_hash(password, method='sha256'))
        login_db.session.add(new_user)
        login_db.session.commit()
        return jsonify({'message' : 'New user created!'})


@api.route('/Stocks/<symbol>')
@api.param('symbol', 'Enter 4 letter company symbol to view details')
class Stocks(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Stock was not found')
    @api.doc(description = 'Get stock details by its symbol')
    @requires_auth
    def get(self, symbol):
        if symbol not in df['Symbol'].tolist():
            api.abort(404, "Stock with symbol \'{}\' doesn't exist".format(symbol))
        return df[df['Symbol'] == symbol].to_dict()
    
 
if __name__ == '__main__':
    df = pd.read_csv('stocks.csv') 
    # print(df.head(3))   
    app.run()
    

