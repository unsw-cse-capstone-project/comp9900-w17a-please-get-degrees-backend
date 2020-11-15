import requests
import datetime

from flask import current_app
from flask_restx import abort

from simvestr.models import Stock, db

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


def get_unix_time():

    date_to = datetime.datetime.now(datetime.timezone.utc)
    date_from = date_to - datetime.timedelta(days=2)

    return int(date_from.timestamp()), int(date_to.timestamp())


def crypto_quote(symbol):
    token = f"&token={current_app.config['FINNHUB_API_KEY']}"
    query_string = QUERYS["crypto"]["candle"]

    date_from, date_to = get_unix_time()
    arg = {
        "symbol": symbol,
        "resolution": "D",
        "to": date_to,
        "from": date_from,
    }
    arg = "&".join([f"{k}={v}" for k, v in arg.items()])
    uri = f"{FINNHUB_BASE}{query_string}{arg}{token}"
    r = requests.get(uri)
    payload = r.json()

    if payload["s"] == "no_data":
        abort(404, "Symbol not found")

    payload = {k: (v[-1] if k not in ("c", "s") else v) for k,v in payload.items()}

    payload["pc"] = payload["c"][0]

    payload["c"] = payload["c"][-1]

    return payload




def finnhub_query(query: str, arg, stock_type="stock"):
    token = f"&token={current_app.config['FINNHUB_API_KEY']}"
    if stock_type == "crypto" and query == "quote":
        return crypto_quote(symbol=arg)
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
    if symbol.strip() == "":
        return abort(400, "Empty symbol string. Symbol must not be empty or whitespace.")
    stock = Stock.query.filter_by(symbol=symbol).first()
    if stock:
        if stock.type == "crypto":
            details = dict(
                exchange=stock.exchange,
                type=stock.type,
                name=stock.name,
                symbol=symbol,
            )
            quote = search(source_api="finnhub", query="quote", arg=symbol)
        else:
            details = search(query="profile", stock_type="stock", arg=symbol)
            if details:
                details["symbol"] = details["ticker"]
                details["industry"] = details["finnhubIndustry"]
                details["type"] = "stock"
                quote = search(source_api="finnhub", query="quote", arg=symbol)
        if stock.last_quote_time is None:
            stock.last_quote = quote["c"]
            stock.last_quote_time = datetime.datetime.utcnow()
            db.session.commit()
        elif stock.last_quote_time > datetime.datetime.utcnow() - datetime.timedelta(minutes=5):
            stock.last_quote = quote["c"]
            stock.last_quote_time = datetime.datetime.utcnow()
            db.session.commit()
    else:
        # BUG: Dont have anything for crypto yet
        details = search(query="profile", stock_type="stock", arg=symbol)
        if details:
            details["symbol"] = details["ticker"]
            details["type"] = "stock"
            details["industry"] = details["finnhubIndustry"]
            quote = search(source_api="finnhub", query="quote", arg=symbol)
            stock = Stock(
                symbol=details["symbol"],
                name=details["name"],
                currency=details["currency"],
                last_quote=quote["c"],
                last_quote_time=datetime.datetime.utcfromtimestamp(quote["t"]),
                industry=details["industry"],
                type="stock",
                display_symbol=details["symbol"],
                exchange=details["exchange"],
            )
            db.session.add(stock)
            db.session.commit()
        else:
            quote = search(query="quote", stock_type="crypto", arg=symbol)
            if quote:
                details = dict(
                    type="crypto",
                    symbol=symbol,
                )
                stock = Stock(
                    symbol=details["symbol"],
                    name=details["symbol"],
                    currency=details["symbol"],
                    last_quote=quote["c"],
                    last_quote_time=datetime.datetime.utcfromtimestamp(quote["t"]),
                    industry="Cryptocurrency/altcoin",
                    type="crypto",
                    display_symbol=details["symbol"],
                    exchange=details["symbol"].split(":")[0],
                )
                db.session.add(stock)
                db.session.commit()

    if details and quote:  # Gives an error - local variable 'details' referenced before assignment
        return {
            **details,
            "quote": quote,
        }
    else:
        return abort(404, "Symbol not found. Please check your inputs.")
