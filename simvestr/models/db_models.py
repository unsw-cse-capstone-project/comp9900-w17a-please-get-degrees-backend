from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

# from simvestr.helpers.db import sql_utcnow

db = SQLAlchemy()

from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

class utcnow(expression.FunctionElement):
    type = DateTime()

@compiles(utcnow, 'sqlite')
def sql_utcnow(**kw):
    return '(DATETIME("now"))'


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


# TODO: Implement a table of permissions for each role.
class User(db.Model):
    __tablename__ = "user"
    ROLE_CHOICES = dict(
        admin="admin",
        user="user"
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(30))

    salt = db.Column(db.String(6), nullable=False)

    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    date_joined = db.Column(db.DateTime, server_default=func.now())
    last_updated = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    validated = db.Column(db.Boolean, default=False)
    role = db.Column(ChoiceType(ROLE_CHOICES), default='user')

    watchlist = db.relationship(
        "Watchlist",
        backref=db.backref("user", lazy="select", uselist=False),
        lazy="select",
        cascade="all, delete-orphan",
        uselist=False
    )

    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolio.id"))
    portfolio = db.relationship(
        "Portfolio",
        backref=db.backref("user", lazy="select", uselist=False),
        lazy='select',
        uselist=False
    )

    def __repr__(self):
        return '<User %r>' % self.email_id


#
# wl_stock = db.Table("watchlist_stock",
#                     db.Column("watchlist_id", db.Integer, db.ForeignKey("watchlist.id")),
#                     db.Column("stock_symbol", db.String, db.ForeignKey("stock.symbol"))
#                     )

p_stock = db.Table("portfolio_stock",
                   db.Column("portfolio_id", db.Integer, db.ForeignKey("portfolio.id")),
                   db.Column("stock_symbol", db.String, db.ForeignKey("stock.symbol"))
                   )


class WatchlistItem(db.Model):
    __tablename__ = "watchlist_item"
    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlist.id'), primary_key=True)
    stock_symbol = db.Column(db.String, db.ForeignKey("stock.symbol"), primary_key=True)
    date_added = db.Column("date_added", db.DateTime, server_default=func.now())


class Watchlist(db.Model):
    __tablename__ = "watchlist"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, server_default=func.now(), )
    watchlist_items = db.relationship("WatchlistItem", backref=db.backref("watchlist", lazy="select", uselist=True),
                                lazy="joined", cascade="all, delete-orphan",)


class Stock(db.Model):
    # TODO: Need to confirm max length of symbol, light research suggests 6
    # TODO: Need to confirm max length of name
    # TODO: Handle crypto currencies codes
    __tablename__ = "stock"
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(15), primary_key=True, nullable=False)
    display_symbol = db.Column(db.String(10), nullable=False, )
    name = db.Column(db.String(200), nullable=False)
    currency = db.Column(db.String(20), nullable=False)
    exchange = db.Column(db.String(200),
                         nullable=False)  # make foreign key in exchanges table or build relationship properly
    last_quote = db.Column(db.Float)
    last_quote_time = db.Column(db.DateTime)
    type = db.Column(db.String(10), default="stock", nullable=False)

    watchlist_items = db.relationship("WatchlistItem", backref=db.backref("stock", lazy="select", uselist=False),
                            lazy="joined", cascade="all, delete-orphan", )

    portfolios = db.relationship("Portfolio", secondary=p_stock, backref=db.backref("stock", lazy="select", ),
                                 lazy="joined")
    transactions = db.relationship("Transaction", backref=db.backref("stock", lazy="select", ), lazy="joined")

    # CHANGE: I think these two can be deleted.
    industry = db.Column(db.String(120), )
    country = db.Column(db.String(120), )


class Portfolio(db.Model):
    __tablename__ = "portfolio"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    portfolio_name = db.Column(db.String(30), nullable=False)

    balance = db.Column(db.Float, nullable=False)

    transactions = db.relationship(
        "Transaction",
        backref=db.backref("portfolio", lazy="select", ),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    stocks = db.relationship("Stock", secondary=p_stock, backref=db.backref("portfolio", lazy="select", ),
                             lazy="joined")


class PortfolioPrice(db.Model):
    __tablename__ = 'portfolioprice'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'))
    portfolio_prices = db.relationship(
        "Portfolio",
        backref=db.backref("portfolioprice", lazy="select", uselist=True, order_by="PortfolioPrice.timestamp"),
        lazy='select',
        uselist=False,
    )

    close_balance = db.Column(db.Float)
    investment_value = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, server_default=func.now(), )


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolio.id"))
    symbol = db.Column(db.String(6), db.ForeignKey("stock.symbol"))  # Should be foreign key in stock table
    quote = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=func.now(), )
    quantity = db.Column(db.Integer, nullable=False)
    fee = db.Column(db.Integer, default=0)


class Exchanges(db.Model):
    code = db.Column(db.String(10), primary_key=True, )
    name = db.Column(db.String(60), )
    is_crypto = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.Integer, )
