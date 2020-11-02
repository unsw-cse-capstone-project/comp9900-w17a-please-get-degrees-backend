import time
from datetime import datetime

import pandas as pd

from simvestr.models import User, Transaction, Stock, Portfolio, PortfolioPrice, db
from simvestr.helpers.search import search

S_PER_MIN = 60

def all_stocks_balance(user: User):
    all_stocks = user.portfolio.transactions.with_entities(
        db.func.sum(Transaction.quantity).label("balance"),
        Transaction.symbol
    ).group_by("symbol").all()

    return {n: q for (q, n) in all_stocks if q > 0}


def stock_balance(user: User, symbol):
    return user.portfolio.transactions.with_entities(
        db.func.sum(Transaction.quantity).label("balance"),
        Transaction.symbol
    ).filter_by(
        symbol=symbol
    ).group_by("symbol").first()


def portfolio_value(user: User, use_stored=False):
    balance = all_stocks_balance(user)
    p_value = dict()

    if use_stored:
        quote = Stock.query.with_entities(
            Stock.symbol,
            Stock.last_quote
        ).filter(Stock.symbol.in_(list(balance.keys()))).all()
        balance_df = pd.DataFrame.from_dict(balance, orient="index", columns=["quantity"])
        quote_df = pd.DataFrame(quote, columns=["symbol", "quote"])
        quote_df.set_index(["symbol"], inplace=True)
        portfolio_df = balance_df.join(quote_df)
        portfolio_df["value"] = portfolio_df.quote * portfolio_df.quantity
        p_value = portfolio_df.to_dict(orient="index",)
    else:
        for stock, quant in balance.items():
            quote = search("quote", stock)["c"]
            p_value[stock] = dict(
                quantity=quant,
                quote=quote,
                value=quote * quant,
            )
    return p_value




def calculate_all_portfolios_values(query_limit=60):
    portfolio_stocks = Stock.query.join(Portfolio, Stock.portfolios).all()
    allowance_per_call = S_PER_MIN/query_limit

    processing_start = time.time()
    # Time logic is to limit our calls per minute to the bandwidth available
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
    all_users = User.query.all()
    for user in all_users:
        portfolio = portfolio_value(user, use_stored=True)
        if not portfolio:
            continue
        portfolio_df = pd.DataFrame.from_dict(portfolio, orient="index",)
        investment_value = portfolio_df["value"].sum()
        cash_balance = user.portfolio.balance
        portfolioprice = PortfolioPrice(
            close_balance=cash_balance,
            investment_value=investment_value,
        )
        user.portfolio.portfolioprice.append(portfolioprice)

        db.session.commit()





