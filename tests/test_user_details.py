import pytest
from tests.conftest import API_URL


def test_user_details(auth, ):
    auth.sign_up()
    auth.login()

    response = auth._client.get(
        "/".join([API_URL, "balance", "user", ""])  # trailing empty space is to get around 308 error
    )

    assert response._status_code == 200
    assert response.get_json()["balance"] == 100000.0


def test_user_balance(auth, ):
    auth.sign_up()
    auth.login()

    response = auth._client.get(
        "/".join([API_URL, "balance", "user", ""])  # trailing empty space is to get around 308 error
    )

    assert response._status_code == 200
    assert response.get_json()["balance"] == 100000.0

# def test_user
