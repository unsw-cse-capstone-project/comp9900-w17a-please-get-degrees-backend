import time
from datetime import datetime, timedelta, timezone

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
        return dict(buy={}, sell={}, )
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
                .drop(["CS", "PN", "id", "portfolio_id", "timestamp", ], axis=1)
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
    average_price(user, )
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


def calculate_all_portfolios_values(query_limit=60,):
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

        portfolio_df = pd.DataFrame.from_records(portfolio, )
        investment_value = portfolio_df["value"].sum()
        cash_balance = user.portfolio.balance

        portfolioprice = PortfolioPrice(
            close_balance=cash_balance, investment_value=investment_value,
        )

        user.portfolio.portfolioprice.append(portfolioprice)

        db.session.commit()


def get_query_time(date, start_hour, start_minute):
    if isinstance(date, int):
        date = datetime.fromtimestamp(date, timezone.utc)
    year, month, day = date.year, date.month, date.day
    compile_time = datetime(year, month, day, start_hour, start_minute, 0, 0, tzinfo=timezone.utc)
    if date > compile_time:
        date = int(compile_time.timestamp())
    else:
        date = (compile_time - timedelta(days=1)).timestamp()

    return int(date)


def simulate(date_from=None, date_to=None, query_limit=60, user=None, start_hour=21, start_minute=30):
    # First, query only the stocks that are in users portfolios
    if user is None:
        portfolio_stocks = Stock.query.join(Portfolio, Stock.portfolios).all()
    else:
        portfolio_stocks = user.portfolio.stocks
    allowance_per_call = S_PER_MIN / query_limit

    if date_to is None:
        date_to = datetime.now(timezone.utc)

    date_to = get_query_time(date_to, start_hour, start_minute)

    if date_from is None:
        date_from = int((date_to - timedelta(weeks=4).total_seconds()))

    date_from = get_query_time(date_from, start_hour, start_minute)

    if date_from > date_to:
        raise ValueError("date_from must be a date at least 1 day before date_to. Check your inputs.")
    elif date_to - date_from < timedelta(days=1).total_seconds():
        raise ValueError("date_from must be a date at least 1 day before date_to. Check your inputs.")

    processing_start = time.time()
    # Time logic is to limit our calls per minute to the bandwidth available
    # Get current quote price for the portfolio stocks

    symbols = [s.symbol for s in portfolio_stocks]
    first_query_flag = True
    for symbol in symbols:
        start_t = time.time()

        arg = {
            "symbol": symbol,
            "resolution": "D",
            "to": date_to,
            "from": date_from,
        }

        quote = search(query="candle", arg=arg)

        if first_query_flag:
            stock_price = pd.DataFrame(
                columns=pd.MultiIndex.from_product([symbols, ["quote", "quantity"]]),
                index=quote["t"]
            )
            first_query_flag = False

        stock_price.loc[:, (symbol, "quote")] = quote["c"]

        end_t = time.time()
        duration = end_t - start_t
        pause_time = allowance_per_call - duration

        if pause_time > 0:
            time.sleep(pause_time)

    # For every user, create a portfolio price entry and commit it to the db
    if user is None:
        all_users = User.query.all()
    else:
        all_users = [user]

    for user in all_users:
        stock_balance = all_stocks_balance(user)
        if not portfolio_stocks:
            continue
        portfolio_stock_symbols = list(stock_balance.keys())
        user_stocks = stock_price[portfolio_stock_symbols]
        for stock, quantity in stock_balance.items():
            user_stocks.loc[:, (stock, "quantity")] = quantity

        investment_values = user_stocks.groupby(axis=1, level=0).prod().sum(axis=1)
        cash_balance = user.portfolio.balance

        payload_df= pd.DataFrame()
        payload_df["timestamp"] = investment_values.index
        payload_df["investment_value"] = investment_values.values
        payload_df["close_balance"] = cash_balance

        payload_df["total_value"] = payload_df.close_balance + payload_df.investment_value

        return payload_df.to_dict("records")



        #Logic to commit to database
        # for timestamp, investment_value in investment_values.iteritems():
        #     portfolioprice = PortfolioPrice(
        #         close_balance=cash_balance,
        #         investment_value=investment_value,
        #         timestamp=timestamp,
        #     )
        #
        #     user.portfolio.portfolioprice.append(portfolioprice)
        #
        # db.session.commit()
