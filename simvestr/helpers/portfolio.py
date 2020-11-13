import time
from datetime import datetime

import pandas as pd
import numpy as np

from simvestr.models import User, Transaction, Stock, Portfolio, PortfolioPrice, db
from simvestr.helpers.search import search

S_PER_MIN = 60


def weighted_avg(df: pd.DataFrame, grouped=False):
    """Expects a dataframe that has symbol, quote, quantity columns"""
    df["total"] = df.quote * df.quantity
    grouped_df = df.groupby("symbol").sum()

    grouped_df["weighted_average"] = grouped_df.total / grouped_df.quantity
    grouped_df["weighted_average_fee"] = grouped_df.fee / grouped_df.quantity
    grouped_df = grouped_df[["weighted_average_fee", "weighted_average", "total"]]
    return grouped_df


# Source: https://stackoverflow.com/questions/50686238/pandas-groupby-with-fifo
def FiFo(dfg):
    if dfg[dfg["CS"] < 0]["quantity"].count():
        subT = dfg[dfg["CS"] < 0]["CS"].iloc[-1]
        dfg["quantity"] = np.where((dfg["CS"] + subT) <= 0, 0, dfg["quantity"])
        dfg = dfg[dfg["quantity"] > 0]
        if len(dfg) > 0:
            dfg["quantity"].iloc[0] = dfg["CS"].iloc[0] + subT
    return dfg


def average_price(user: User, mode="moving"):
    trans_df = pd.read_sql(user.portfolio.transactions.subquery(), db.session.bind)
    if trans_df.empty:
        return dict(buy={}, sell={},)
    buy_df = trans_df[trans_df.quantity > 0]
    sell_df = trans_df[trans_df.quantity < 0]
    if mode == "alltime":
        buy_df = weighted_avg(buy_df)
        sell_df = weighted_avg(sell_df)
        payload = dict(
            buy=buy_df.to_dict(orient="index"), sell=sell_df.to_dict(orient="index")
        )
    elif mode == "moving":
        trans_df["PN"] = np.where(trans_df["quantity"] > 0, "P", "N")
        trans_df["CS"] = trans_df.groupby(["symbol", "PN"])["quantity"].cumsum()
        fifo_trans_df = (
            trans_df.groupby(["symbol"])
            .apply(FiFo)
            .drop(["CS", "PN", "id", "portfolio_id", "timestamp",], axis=1)
            .reset_index(drop=True)
        )
        moving_avg_df = weighted_avg(fifo_trans_df, grouped=True)
        payload = dict(buy=moving_avg_df.to_dict(orient="index"), sell={})
    return payload


def all_stocks_balance(user: User):
    all_stocks = (
        user.portfolio.transactions.with_entities(
            db.func.sum(Transaction.quantity).label("balance"), Transaction.symbol
        )
        .group_by("symbol")
        .all()
    )

    return {n: q for (q, n) in all_stocks if q > 0}


def stock_balance(user: User, symbol):
    average_price(user,)
    return (
        user.portfolio.transactions.with_entities(
            db.func.sum(Transaction.quantity).label("balance"), Transaction.symbol
        )
        .filter_by(symbol=symbol)
        .group_by("symbol")
        .first()
    )


def portfolio_value(user: User, use_stored=False, average_mode="moving"):
    balance = all_stocks_balance(user)
    avgs = average_price(user, mode=average_mode)

    p_value = []

    if use_stored:
        quote = (
            Stock.query.with_entities(Stock.symbol, Stock.last_quote)
            .filter(Stock.symbol.in_(list(balance.keys())))
            .all()
        )
        balance_df = pd.DataFrame.from_dict(
            balance, orient="index", columns=["quantity"]
        )
        quote_df = pd.DataFrame(quote, columns=["symbol", "current"])
        quote_df.set_index(["symbol"], inplace=True)
        portfolio_df = balance_df.join(quote_df)

        portfolio_df["value"] = portfolio_df.current * portfolio_df.quantity
        p_value = (
            portfolio_df.reset_index()
            .rename(columns={"index": "symbol"})
            .to_dict(orient="records")
        )

    else:
        for stock, quant in balance.items():
            quote = search("quote", stock)
            current = quote["c"]
            previous = quote["pc"]
            p_value.append(
                dict(
                    symbol=stock,
                    quantity=quant,
                    current=current,
                    previous=previous,
                    value=current * quant,
                )
            )
    for entry in p_value:
        for trade_type, stock_statistics in avgs.items():
            entry[trade_type] = {}
            if entry["symbol"] in stock_statistics:
                entry[trade_type] = stock_statistics[entry["symbol"]]
        entry["return"] = entry["value"] - entry["buy"]["total"]

    return p_value


def get_portfolio(user, averagemode):
    portfolio = portfolio_value(user, average_mode=averagemode.lower())
    return dict(
        name=user.portfolio.portfolio_name,
        balance=user.portfolio.balance,
        total_value=sum([x["value"] for x in portfolio]),
        total_return=sum([x["return"] for x in portfolio]),
        portfolio=portfolio,
    )


def get_stocks_owned(user: User):
    stocks_owned = all_stocks_balance(user)
    payload = dict(
        stocksowned=[dict(symbol=k, quantity=v) for k, v in stocks_owned.items()]
    )
    return payload


def get_close_balance(user: User, number_of_days=7):
    portfolios = user.portfolio.portfolioprice[-number_of_days:]
    payload = dict(
        history=[
            dict(
                close_balance=p.close_balance,
                investment_value=p.investment_value,
                total_value=(p.close_balance + p.investment_value),
                timestamp=int(p.timestamp.timestamp()),
            )
            for p in portfolios
        ]
    )
    return payload


def calculate_all_portfolios_values(query_limit=60, new_day=None):
    # First, query only the stocks that are in users portfolios
    portfolio_stocks = Stock.query.join(Portfolio, Stock.portfolios).all()
    allowance_per_call = S_PER_MIN / query_limit

    processing_start = time.time()
    # Time logic is to limit our calls per minute to the bandwidth available
    # Get current quote price for the portfolio stocks
    for stock in portfolio_stocks:
        start_t = time.time()

        quote = search("quote", stock.symbol)

        stock.last_quote = quote["c"]
        stock.last_quote_time = datetime.now()

        end_t = time.time()
        duration = end_t - start_t
        pause_time = allowance_per_call - duration

        if pause_time > 0:
            time.sleep(pause_time)
    db.session.commit()
    # For every user, create a portfolio price entry and commit it to the db
    all_users = User.query.all()
    for user in all_users:
        portfolio = portfolio_value(user, use_stored=True)
        if not portfolio:
            continue

        portfolio_df = pd.DataFrame.from_records(portfolio,)
        investment_value = portfolio_df["value"].sum()
        cash_balance = user.portfolio.balance
        if new_day:
            portfolioprice = PortfolioPrice(
                close_balance=cash_balance,
                investment_value=investment_value,
                timestamp=new_day,
            )
        else:
            portfolioprice = PortfolioPrice(
                close_balance=cash_balance, investment_value=investment_value,
            )

        user.portfolio.portfolioprice.append(portfolioprice)

        db.session.commit()
