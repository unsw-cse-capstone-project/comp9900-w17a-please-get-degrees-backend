from simvestr.models import db
from simvestr.models import User, Watchlist, Stock, Portfolio, PortfolioPrice, Transaction, Exchanges
from simvestr.helpers.search import search

from pathlib import Path
import pandas as pd
import heapq
import click
import requests

import numpy as np

from flask import current_app, g
from flask.cli import with_appcontext

from werkzeug.security import generate_password_hash

SALT_SIZE = 6
def make_salt():
    valid_pw_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXY0123456789!@#$%^&*()-_=+<>,./?:;{}[]`~"

    return "".join(np.random.choice(list(valid_pw_chars),size=SALT_SIZE))

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
    db = get_db()
    db.create_all()


def delete_db():
    curr_dir = Path.cwd()
    db_path = curr_dir / "instance" / "simvestr.db"
    db_path.unlink()


def bulk_add_from_df(df, db, model):
    df = df.replace({np.nan: None})
    df.columns = df.columns.str.lower()
    # mapping = df.to_dict(orient="records")
    db.session.bulk_insert_mappings(
        model,
        df.to_dict(orient="records")
    )
    db.session.commit()


def populate_stocks():


    db = get_db()

    non_crypto_exchanges = Exchanges.query.filter(
        Exchanges.is_crypto==False, Exchanges.priority != None).all()
    crypto_exchanges = Exchanges.query.filter(
        Exchanges.is_crypto==True, Exchanges.priority != None).all()

    exchanges = {
        "stock": {
            "exchange": non_crypto_exchanges,
            "name": {
                "displaySymbol": "display_symbol",
                "description": "name"
            },
            "search": lambda ex: search(query="exchange", arg=ex)
        },
        # "crypto": {
        #     "exchange": crypto_exchanges,
        #     "name": {
        #         "description": "name",
        #         "displaySymbol": "currency",  # please review, unsure if this is a good idea
        #     },
        #     "search": lambda ex: search(query="exchange", arg=ex, stock_type="crypto")
        # },
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
                (exchange.priority,  {exchange: df})
            )

    while exchange_stocks:
        num_stocks, stock_dict = heapq.heappop(exchange_stocks)
        ex, df = stock_dict.popitem()
        unique_stocks = df.name.unique()
        sq = Stock.query.filter(Stock.name.in_(list(unique_stocks))).all()

        if sq:
            names = [n.name for n in sq]
            df = df[~df.name.isin(names)]

        if len(df):
            bulk_add_from_df(df, db, Stock)


def load_dummy():
    db = get_db()
    data_path = Path.cwd() / "resources" / "test_data_user.xlsx"

    # Order of models matterss
    load_mapping = dict(
        exchanges=Exchanges,
        watchlist=Watchlist,
        portfolio=Portfolio,
        portfolioprice=PortfolioPrice,
        transaction=Transaction,
        users=User,
    )

    df_map = {k:pd.read_excel(data_path, sheet_name=k) for k in load_mapping.keys()}

    bulk_add_from_df(df_map['exchanges'], db, Exchanges)
    bulk_add_from_df(df_map['portfolioprice'], db, PortfolioPrice)
    bulk_add_from_df(df_map['transaction'], db, Transaction)

    populate_stocks()


    for idx, user_row in df_map['users'].iterrows():
        user = User(**user_row.dropna().to_dict())
        db.session.add(user)
        db.session.commit()

        watch_df = df_map['watchlist']
        watch_df = watch_df[watch_df.user_id==user.id]
        watchlist = Watchlist(user_id=user.id)


        stocks = Stock.query.filter(Stock.symbol.in_(list(watch_df["symbol"].values))).all()
        watchlist.stocks = stocks

        db.session.add(watchlist)

        user.watchlist = watchlist
        db.session.commit()
        # db.session.add(watchlist)

        # for idx, wl_row in watch_df.iterrows():
        #     wl_data = wl_row[wl_row.index.difference(["symbol"])]
        #     watchlist = Watchlist(**wl_data.to_dict())
        #
        #     stocks = Stock.query.filter(Stock.symbol.in_(list(watch_df["symbol"].values))).all()
        #     watchlist.stocks = stocks


    # for sheet, model in load_mapping.items():
    #     df = pd.read_excel(data_path, sheet_name=sheet)
    #     if sheet == "users":
    #         df['salt'] = [make_salt() for _ in range(len(df))]
    #         df.password = df.password + df.salt
    #         df.password = df.password.apply(generate_password_hash, method="sha256")
    #
    #     bulk_add_from_df(df, db, model)
    # db.session.close()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
