from simvestr.models import db
from simvestr.models import User, Watchlist, Stock, Portfolio, PortfolioPrice, Transaction, Exchanges


from pathlib import Path
import pandas as pd
import numpy as np
from flask import current_app, g
import click
from flask.cli import with_appcontext
import requests


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
    db.session.bulk_insert_mappings(
        model,
        df.to_dict(orient="records")
    )
    db.session.commit()


def populate_stocks():


    db = get_db()

    non_crypto_exchanges = Exchanges.query.with_entities(Exchanges.code).filter_by(is_crypto=False).all()
    crypto_exchanges = Exchanges.query.with_entities(Exchanges.code).filter_by(is_crypto=True).all()
    SYMBOL_ALL_API = lambda \
            ex: f"https://finnhub.io/api/v1/stock/symbol?exchange={ex}&" \
                f"token={current_app.config['FINNHUB_API_KEY']}"
    CRYPTO_SYMBOL_ALL_API = lambda \
            ex: f"https://finnhub.io/api/v1/crypto/symbol?exchange={ex}&" \
                f"token={current_app.config['FINNHUB_API_KEY']}"
    non_crypto_exchanges = [x[0] for x in non_crypto_exchanges]
    crypto_exchanges = [x[0] for x in crypto_exchanges]
    for exchange in non_crypto_exchanges:
        r = requests.get(SYMBOL_ALL_API(exchange))
        df = pd.DataFrame.from_records(r.json())
        df["is_crypto"] = False
        df["exchange"] = exchange
        if "type" in df.columns:
            df.drop(columns=["type"], inplace=True)
        name_map = {
            "displaySymbol":"display_symbol",
            "description": "name"
        }
        df.rename(columns=name_map, inplace=True)

        bulk_add_from_df(df, db, Stock)

    for exchange in crypto_exchanges:
        r = requests.get(CRYPTO_SYMBOL_ALL_API(exchange))
        df = pd.DataFrame.from_records(r.json())
        df["is_crypto"] = True
        df["display_symbol"] = df["displaySymbol"]
        df["exchange"] = exchange
        name_map = {
            "description":"name",
            "displaySymbol": "currency",#please review, unsure if this is a good idea
        }
        df.rename(columns=name_map, inplace=True)
        bulk_add_from_df(df, db, Stock)


def load_dummy():
    db = get_db()
    data_path = Path.cwd() / "resources" / "test_data_user.xlsx"

    # Order of models matterss
    load_mapping = dict(
        users=User,
        # stock=Stock,
        watchlist=Watchlist,
        portfolio=Portfolio,
        portfolioprice=PortfolioPrice,
        transaction=Transaction,
        exchanges=Exchanges
    )

    for sheet, model in load_mapping.items():
        df = pd.read_excel(data_path, sheet_name=sheet)
        bulk_add_from_df(df, db, model)
    db.session.close()

    populate_stocks()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
