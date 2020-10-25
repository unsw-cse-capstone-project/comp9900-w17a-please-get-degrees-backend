from flask import current_app
from flask_restx import abort
import requests

FINNHUB_BASE = "https://finnhub.io/api/v1/"

QUERYS = dict(
    stock=dict(
        exchange="stock/symbol?exchange=",
        profile="stock/profile2?symbol=",
        quote="quote?symbol=",
    ),
    crypto=dict(
        exchange="crypto/symbol?exchange=",
        quote="quote?symbol=",
    )
)

STOCK_TYPE_MAP = {True: "CRYPTO", False: "STOCK"}


def finnhub_query(query: str, arg, stock_type="stock"):
    token = f'&token={current_app.config["FINNHUB_API_KEY"]}'
    try:
        query_string = QUERYS[stock_type][query]
    except ValueError as e:
        abort(400, e)
    uri = f"{FINNHUB_BASE}{query_string}{arg}{token}"
    return requests.get(uri).json()

search_function = {'finnhub':finnhub_query}

def search(source_api, query, arg, stock_type="stock"):
    if source_api not in search_function:
        raise NotImplementedError("Api not supported")

    return search_function[source_api](query, arg, stock_type)