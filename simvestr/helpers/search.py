from flask import current_app
from flask_restx import abort
import requests

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
