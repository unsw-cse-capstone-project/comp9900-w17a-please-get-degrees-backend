import pytest
from tests.conftest import API_URL


def test_add(registered_user):
    client = registered_user._client

    param = {
        "symbol": "AMZN"
    }

    response = client.post(
        "/".join([API_URL, "watchlist", ]),
        json=param
    )

    assert response.status_code == 201

    response = client.post(
        "/".join([API_URL, "watchlist", ]),
        json=param
    )

    assert response.status_code == 200


def test_bad_add(registered_user):
    client = registered_user._client

    param = {
        "symbol": "APPL"
    }

    response = client.post(
        "/".join([API_URL, "watchlist", ]),
        json=param
    )

    assert response.status_code == 404


def test_delete(registered_user):
    client = registered_user._client

    param = {
        "symbol": "AMZN"
    }

    client.post(
        "/".join([API_URL, "watchlist", ]),
        json=param
    )

    response = client.delete(
        "/".join([API_URL, "watchlist", ]),
        json=param
    )

    assert response.status_code == 201

    response = client.delete(
        "/".join([API_URL, "watchlist", ]),
        json=param
    )

    assert response.status_code == 200

@pytest.mark.parametrize(("symbol", "code",), (
        ("", 400),
        ("aapl", 200),
        ("appl", 404),
))
def test_bad_delete(registered_user, symbol, code):
    client = registered_user._client

    param = {
        "symbol": symbol
    }

    response = client.delete(
        "/".join([API_URL, "watchlist", ]),
        json=param
    )

    assert response.status_code == code
