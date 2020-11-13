import pytest
from tests.conftest import API_URL, get_quote


@pytest.mark.parametrize(("symbol", "quote", "trade_type", "quantity", "message"), (
        ("aapl", None, "buy", 10000, "Insufficient funds"),
        ("aapl", -1, "buy", 1, "Current price has changed, can't commit this transaction"),
        ("aapl", None, "buy", -1, "Quantity should be an integer value greater than 0"),
        ("appl", 1, "buy", 1, "Symbol not found."),
))
def test_bad_buy(registered_user, symbol, quote, trade_type, quantity, message):
    client = registered_user._client

    if quote is None:
        quote = get_quote(client, symbol)
        quote = quote["quote"]["c"]

    buy = {
        "symbol": symbol,
        "quote": quote,
        "trade_type": trade_type,
        "quantity": quantity,
    }

    response = client.post(
        "/".join([API_URL, "marketorder",]),
        json=buy
    )

    assert message in response.json["message"]


@pytest.mark.parametrize(("symbol", "quote", "trade_type", "quantity",), (
        ("aapl", None, "buy", 5,),
        ("tsla", None, "buy", 1,),
        ("BINANCE:BTCUSDT", None, "buy", 2,),
        ("BINANCE:ETHBTC", None, "buy", 1, ),
))
def test_good_buy(registered_user, symbol, quote, trade_type, quantity,):
    client = registered_user._client

    if quote is None:
        quote = get_quote(client, symbol)
        quote = quote["quote"]["c"]

    buy = {
        "symbol": symbol,
        "quote": quote,
        "trade_type": trade_type,
        "quantity": quantity,
    }

    response = client.post(
        "/".join([API_URL, "marketorder",]),
        json=buy
    )

    assert message == response.json


# @pytest.mark.parametrize(
#     ("symbol", "quote", "trade_type", "sell_quantity", "buy_quantity", "message"),
#     (
#             ("aapl", None, "sell", 2, 1, "Insufficient quantity of stock to sell"),
#             ("aapl", -1, "sell", 1, 1, "Current price has changed, can't commit this transaction"),
#             ("aapl", None, "sell", -1, 1, "Quantity should be an integer value greater than 0"),
#             ("appl", 1, "sell", 1, None, "Symbol not found."),
#             ("tsla", None, "sell", 1, 0, "You currently don't own this stock"),
#     )
# )
# def test_bad_sell(registered_user, symbol, quote, trade_type, sell_quantity, buy_quantity, message):
#     client = registered_user._client
#
#     if buy_quantity:
#         registered_user.buy(quantity=buy_quantity, symbol=symbol)
#
#     if quote is None:
#         quote = get_quote(client, symbol)
#         quote = quote["quote"]["c"]
#
#     sell = {
#         "symbol": symbol,
#         "quote": quote,
#         "trade_type": trade_type,
#         "quantity": sell_quantity,
#     }
#
#     response = client.post(
#
#         "/".join([API_URL, "marketorder", ]),
#         json=sell
#     )
#
#     assert message in response.json["message"]
