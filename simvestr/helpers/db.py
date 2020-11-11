from pathlib import Path
import pandas as pd
import heapq
import click

import numpy as np

from flask import current_app, g
from flask.cli import with_appcontext

from werkzeug.security import generate_password_hash

from simvestr import create_app
from simvestr.models import db
from simvestr.models import User, Watchlist, Stock, Portfolio, PortfolioPrice, Transaction, Exchanges
from simvestr.helpers.search import search
from simvestr.helpers.portfolio import all_stocks_balance

SALT_SIZE = 6


def make_salt():
    valid_pw_chars = current_app.config["VALID_CHARS"]

    return "".join(np.random.choice(list(valid_pw_chars), size=SALT_SIZE))


# Defines setup and tear down the database

def get_db():
    if "b" not in g:
        db.init_app(current_app)
        g.db = db

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db.create_all()


def delete_db():
    curr_dir = Path.cwd()
    db_path = curr_dir / "instance" / "simvestr.db"
    if db_path.is_file():
        db_path.unlink()


def bulk_add_from_df(df, db, model):
    df = df.replace({np.nan: None})
    df.columns = df.columns.str.lower()
    db.session.bulk_insert_mappings(
        model,
        df.to_dict(orient="records")
    )
    db.session.commit()


def populate_stocks():
    non_crypto_exchanges = Exchanges.query.filter(
        Exchanges.is_crypto == False, Exchanges.priority != None).all()
    crypto_exchanges = Exchanges.query.filter(
        Exchanges.is_crypto == True, Exchanges.priority != None).all()

    exchanges = {
        "stock": {
            "exchange": non_crypto_exchanges,
            "name": {
                "displaySymbol": "display_symbol",
                "description": "name"
            },
            "search": lambda ex: search(query="exchange", arg=ex)
        },
        "crypto": {
            "exchange": crypto_exchanges,
            "name": {
                "description": "name",
                "displaySymbol": "currency",  # please review, unsure if this is a good idea
            },
            "search": lambda ex: search(query="exchange", arg=ex, stock_type="crypto")
        },
    }

    exchange_stocks = []
    heapq.heapify(exchange_stocks)
    for ex_type, exchange_dict in exchanges.items():
        for exchange in exchange_dict["exchange"]:
            payload = exchange_dict["search"](exchange.code)
            df = pd.DataFrame.from_records(payload)
            df["exchange"] = exchange.code
            df["type"] = ex_type
            df.rename(columns=exchange_dict["name"], inplace=True)
            if ex_type == 'crypto':
                df['display_symbol'] = df.currency
            heapq.heappush(
                exchange_stocks,
                (exchange.priority, {exchange: df})
            )

    while exchange_stocks:
        num_stocks, stock_dict = heapq.heappop(exchange_stocks)
        ex, df = stock_dict.popitem()
        unique_stocks = df.name.unique()
        sq = Stock.query.filter(Stock.symbol.in_(list(unique_stocks))).all()

        if sq:
            symbols = [n.symbol for n in sq]
            df = df[~df.symbol.isin(symbols)]

        if len(df):
            bulk_add_from_df(df, db, Stock)


def load_dummy(data_path: Path):
    db = get_db()

    # Order of models matters
    load_mapping = dict(
        exchanges=Exchanges,
        watchlist=Watchlist,
        portfolio=Portfolio,
        portfolioprice=PortfolioPrice,
        transaction=Transaction,
        users=User,
    )

    df_map = {k: pd.read_excel(data_path, sheet_name=k) for k in load_mapping.keys()}

    df_map["users"]['salt'] = [make_salt() for _ in range(len(df_map["users"]))]
    df_map["users"].password = df_map["users"].password + df_map["users"].salt
    df_map["users"].password = df_map["users"].password.apply(generate_password_hash, method="sha256",)

    bulk_add_from_df(df_map["exchanges"], db, Exchanges)
    bulk_add_from_df(df_map["transaction"], db, Transaction)

    populate_stocks()

    for idx, user_row in df_map['users'].iterrows():

        user = User(**user_row.dropna().to_dict())
        db.session.add(user)
        db.session.commit()

        watch_df = df_map["watchlist"]
        watch_df = watch_df[watch_df.user_id == user.id]
        watchlist = Watchlist(user_id=user.id)

        stocks = Stock.query.filter(Stock.symbol.in_(list(watch_df["symbol"].values))).all()
        watchlist.stocks = stocks

        db.session.add(watchlist)

        user.watchlist = watchlist

        db.session.commit()

        port_df = df_map["portfolio"]
        port_df = port_df[port_df.user_id == user.id]
        port = Portfolio(**port_df[["portfolio_name", "balance"]].to_dict(orient="records")[0])
        port.transactions = []

        db.session.add(port)

        user.portfolio = port

        db.session.commit()

        portprice_df = df_map["portfolioprice"]
        portprice_df = portprice_df[portprice_df.user_id == user.id]
        portprice = PortfolioPrice(
            **portprice_df[portprice_df.columns.difference(["user_id", "portfolio_id"])].to_dict(orient='records')[0]
        )

        db.session.add(portprice)

        port.portfolioprice.append(portprice)

        db.session.commit()

        trans_df = df_map["transaction"]
        trans_df = trans_df[trans_df.user_id == user.id]
        trans_df = trans_df[trans_df.columns.difference(["user_id", "portfolio_id"])]

        stocks = Stock.query.filter(Stock.symbol.in_(list(trans_df["symbol"].unique()))).all()
        stock_dict = {s.symbol: s for s in stocks}
        transactions = Transaction.query.filter_by(portfolio_id=user.portfolio.id).all()
        for trans in transactions:
            trans.stock = stock_dict[trans.symbol]
            port.transactions.append(trans)

            db.session.add(trans)
            db.session.commit()

        curr_balance = all_stocks_balance(user)
        stock_list = Stock.query.filter(Stock.symbol.in_(list(curr_balance))).all()
        user.portfolio.stocks.extend(stock_list)

        db.session.commit()



@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def setup_new_db(data_path: Path):
    app = create_app()

    with app.app_context():
        delete_db()
        init_db()
        load_dummy(data_path)