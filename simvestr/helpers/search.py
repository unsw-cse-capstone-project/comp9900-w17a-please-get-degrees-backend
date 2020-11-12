import requests
import datetime

from flask import current_app
from flask_restx import abort

from simvestr.models import Stock

FINNHUB_BASE = "https://finnhub.io/api/v1/"

ENCODING = "utf-8"

QUERYS = dict(
    stock=dict(
        exchange="stock/symbol?exchange=",
        profile="stock/profile2?symbol=",
        quote="quote?symbol=",
        candle="stock/candle?",
    ),
    crypto=dict(
        exchange="crypto/symbol?exchange=",
        candle="crypto/candle?",
    )
)

STOCK_TYPE_MAP = {True: "CRYPTO", False: "STOCK"}


def finnhub_query(query: str, arg, stock_type="stock"):
    token = f"&token={current_app.config['FINNHUB_API_KEY']}"
    try:
        query_string = QUERYS[stock_type][query]
    except ValueError as e:
        abort(400, e)
    uri = f"{FINNHUB_BASE}{query_string}{arg}{token}"
    r = requests.get(uri)
    if r.content.decode(ENCODING) == "You don't have access to this resource.":
        abort(401, r.content.decode(ENCODING))
    return r.json()


search_function = {"finnhub": finnhub_query}


def search(query, arg, stock_type="stock", source_api="finnhub"):
    if source_api not in search_function:
        raise NotImplementedError("Api not supported")

    if query == "candle":
        arg = "&".join([f"{k}={v}" for k, v in arg.items()])

    return search_function[source_api](query, arg, stock_type)


def get_details(symbol):
    stock = Stock.query.filter_by(symbol=symbol).first()  # If its in the database, we know where to get it

    if stock:
        if stock.type == "crypto":
            current_unix_time = datetime.datetime.now().timestamp()
            current_price_quote_args = {
                "symbol": symbol,
                "resolution": "1",
                "to": int(current_unix_time),
                "from": int(current_unix_time - datetime.timedelta(minutes=1).total_seconds()),
            }
            previous_price_quote_args = {
                "symbol": symbol,
                "resolution": "D",
                "to": int(current_unix_time - datetime.timedelta(days=1).total_seconds()),
                "from": int(current_unix_time - datetime.timedelta(days=2).total_seconds()),
            }
            details = dict(
                exchange=stock.exchange,
                type=stock.type,
                name=stock.name,
                symbol=symbol,
            )
            quote = search(source_api="finnhub", query="candle", arg=current_price_quote_args)
            pc_quote = search(source_api="finnhub", query="candle", arg=previous_price_quote_args)
            if quote:
                quote = {k: v[0] for k, v in quote.items()}
                quote["pc"] = pc_quote["c"][0]
        else:
            details = search(query="profile", stock_type="stock", arg=symbol)
            if details:
                details["symbol"] = details["ticker"]
                details["industry"] = details["finnhubIndustry"]
                details["type"] = "stock"
                quote = search(source_api="finnhub", query="quote", arg=symbol)
    else:
        details = search(query="profile", stock_type="stock", arg=symbol)
        if details:
            details["symbol"] = details["ticker"]
            details["type"] = "stock"
            details["industry"] = details["finnhubIndustry"]
            quote = search(source_api="finnhub", query="quote", arg=symbol)


    payload = {}
    if details and quote:  # Gives an error - local variable 'details' referenced before assignment
        payload = {
            **details,
            "quote": quote,
        }
    else:
        return abort(404, "Symbol not found. Please check your inputs.")
    return payload
