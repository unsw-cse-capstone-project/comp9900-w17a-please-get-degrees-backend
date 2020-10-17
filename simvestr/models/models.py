from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()



# from here: https://stackoverflow.com/questions/6262943/sqlalchemy-how-to-make-django-choices-using-sqlalchemy
class ChoiceType(db.TypeDecorator):
    ''' Use this class to create multiple choices for a model'''
    impl = db.String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.items() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]

#TODO: Implement a table of permissions for each role.
class User(db.Model):
    ROLE_CHOICES = dict(
        admin='admin',
        user='user'
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(30))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    date_joined = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    validated = db.Column(db.Boolean, default=False)
    role = db.Column(ChoiceType(ROLE_CHOICES))
    
    watchlist = db.relationship("Watchlist", backref='user', lazy='dynamic', cascade="all, delete-orphan",)#need similar for portfolio, except it will be 1-m
    portfolio = db.relationship("Portfolio", backref='user', lazy='dynamic', cascade="all, delete-orphan",)
    portfolioprice = db.relationship("PortfolioPrice", backref='user', lazy='dynamic', cascade="all, delete-orphan",)
    transaction = db.relationship("Transaction", backref='user', lazy='dynamic', cascade="all, delete-orphan",)
    
    def __repr__(self):
        return '<User %r>' % self.email_id


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    stock_symbol = db.Column(db.Integer, db.ForeignKey('stock.symbol'))
    timestamp = db.Column(db.DateTime, default=datetime.now,)


class Stock(db.Model):
    #TODO: Need to confirm max length of symbol, light research suggests 6
    #TODO: Need to confirm max length of name
    #TODO: Handle crypto currencies codes
    symbol = db.Column(db.String(6), unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    exchange = db.Column(db.String(200),)
    industry = db.Column(db.String(120),)
    country = db.Column(db.String(120),)


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    portfolio_name = db.Column(db.String(30), nullable=False)
    portfolio_price = db.relationship("PortfolioPrice", backref='portfolio', lazy='dynamic', cascade="all, delete-orphan",)
    transaction = db.relationship("Transaction", backref='portfolio', lazy='dynamic', cascade="all, delete-orphan",)
        
    def __repr__(self):
        return '<Portfolio %r>' % self.portfolio_name
    
    
class PortfolioPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    close_balance = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.now,)
    
    
class Transaction(db.Model):
    TRADE_CHOICES = dict(
        buy='buy',
        sell='sell',
        settled='settled'
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.portfolio_id'))
    symbol = db.Column(db.String(6), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    trade_type = db.Column(ChoiceType(TRADE_CHOICES))
    timestamp = db.Column(db.DateTime, default=datetime.now,)
    quantity = db.Column(db.Integer, nullable=False)
    fee = db.Column(db.Integer, default=0)
