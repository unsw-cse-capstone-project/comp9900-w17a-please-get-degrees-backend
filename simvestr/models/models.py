from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

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


# TODO: Implement a table of permissions for each role.
class User(db.Model):
    __tablename__ = 'user'
    ROLE_CHOICES = dict(
        admin='admin',
        user='user'
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(30))

    salt = db.Column(db.String(6), nullable=False)

    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    date_joined = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    validated = db.Column(db.Boolean, default=False)
    role = db.Column(ChoiceType(ROLE_CHOICES), default='user')

    watchlist = db.relationship(
        "Watchlist",
        backref=db.backref("user", lazy="select", uselist=False),
        lazy='select',
        cascade="all, delete-orphan",
        uselist=False
    )

    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'))
    portfolio = db.relationship(
        "Portfolio",
        backref=db.backref("user", lazy="select", uselist=False),
        lazy='select',
        uselist=False
    )

    def __repr__(self):
        return '<User %r>' % self.email_id


wl_stock = db.Table('watchlist_stock',
                    db.Column('watchlist_id', db.Integer, db.ForeignKey('watchlist.id')),
                    db.Column('stock_symbol', db.String, db.ForeignKey('stock.symbol'))
                    )

p_stock = db.Table('portfolio_stock',
                   db.Column('portfolio_id', db.Integer, db.ForeignKey('portfolio.id')),
                   db.Column('stock_symbol', db.String, db.ForeignKey('stock.symbol'))
                   )


class Watchlist(db.Model):
    __tablename__ = "watchlist"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    stocks = db.relationship("Stock", secondary=wl_stock, backref=db.backref("watchlist", lazy="select", ),
                             lazy="joined")
    timestamp = db.Column(db.DateTime, default=datetime.now, )


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
    type = db.Column(db.String(10), default="stock", nullable=False)

    watchlists = db.relationship("Watchlist", secondary=wl_stock, backref=db.backref("stock", lazy="select", ),
                                 lazy="joined")
    portfolios = db.relationship("Portfolio", secondary=p_stock, backref=db.backref("stock", lazy="select", ),
                                 lazy="joined")
    transactions = db.relationship("Transaction", backref=db.backref("stock", lazy="select", ), lazy="joined")

    # CHANGE: I think these two can be deleted.
    industry = db.Column(db.String(120), )
    country = db.Column(db.String(120), )


class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    portfolio_name = db.Column(db.String(30), nullable=False)

    transactions = db.relationship(
        "Transaction",
        backref=db.backref("portfolio", lazy="select", ),
        lazy='dynamic',
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
    
    close_balance = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.now, )


class Transaction(db.Model):
    TRADE_CHOICES = dict(
        buy='buy',
        sell='sell',
        settled='settled'
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'))
    symbol = db.Column(db.String(6), db.ForeignKey('stock.symbol'))  # Should be foreign key in stock table
    quote = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, )
    quantity = db.Column(db.Integer, nullable=False)
    fee = db.Column(db.Integer, default=0)


class Exchanges(db.Model):
    code = db.Column(db.String(10), primary_key=True, )
    name = db.Column(db.String(60), )
    is_crypto = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.Integer, )
