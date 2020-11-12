import pytest
from tests.conftest import API_URL

@pytest.mark.parametrize(("symbol", "quote", "trade_type", "quantity", "message"), (
        ("aapl", 100, "buy", 10000, "Insufficient funds"),
        ("aapl", -1, "buy", 1, "Current price has changed, can't commit this transaction"),
        ("aapl", 1, "buy", -1, "Quantity should be an integer value greater than 0"),
        ("appl", 1, "buy", 1, "Symbol not found."),
))
def test_bad_buy(registered_user, symbol, quote, trade_type, quantity, message):
    client = registered_user._client

    buy = {
        "symbol":symbol,
        "quote":quote,
        "trade_type":trade_type,
        "quantity":quantity,
    }

    response = client.post(
        "/".join([API_URL, "marketorder",]),
        json=buy
    )

    assert message in response.json["message"]
