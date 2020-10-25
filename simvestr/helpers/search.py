from flask import current_app
import requests

FINNHUB_BASE = "https://finnhub.io/api/v1/"

QUERYS = dict(
    dict(
        exchange="stock/symbol?exchange=",
        profile="stock/profile2?symbol=",
        quote="quote?symbol=",
    )
)

STOCK_TYPE_MAP = {True: "CRYPTO", False: "STOCK"}




def finnhub_query(query: str, arg):
    token = f'&token={current_app.config["FINNHUB_API_KEY"]}'
    query_string = QUERYS[query]
    uri = f"{FINNHUB_BASE}{query_string}{arg}{token}"
    return requests.get(uri).json()

search_function = {'finnhub':finnhub_query}

def search(source_api, query, arg):
    if source_api not in search_function:
        raise NotImplementedError("Api not supported")

    return search_function[source_api](query, arg)