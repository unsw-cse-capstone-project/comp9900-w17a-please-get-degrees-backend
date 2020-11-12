import pytest
from tests.conftest import API_URL


def test_user_details(auth, ):
    auth.sign_up()
    auth.login()

    response = auth._client.get(
        "/".join([API_URL, "user", "info"])  # trailing empty space is to get around 308 error
    )

    assert response._status_code == 200
    assert response.get_json()["first_name"] == auth.first_name
    assert response.get_json()["last_name"] == auth.last_name
    assert response.get_json()["email"] == auth.email

def test_user_change_details(auth, ):
    auth.sign_up()
    auth.login()

    change_names = dict(
        first_name="John",
        last_name="Smith",
    )

    auth.first_name = change_names["first_name"]
    auth.last_name = change_names["last_name"]


    response = auth._client.put(
        "/".join([API_URL, "changedetails", "changenames"]),
        json=change_names
    )

    assert response._status_code == 200

    response = auth._client.get(
        "/".join([API_URL, "user", "info"])  # trailing empty space is to get around 308 error
    )

    assert response._status_code == 200
    assert response.get_json()["first_name"] == auth.first_name
    assert response.get_json()["last_name"] == auth.last_name
    assert response.get_json()["email"] == auth.email


def test_user_change_password(auth, ):
    auth.sign_up()
    auth.login()

    change_names = dict(
        first_name="John",
        last_name="Smith",
    )

    auth.first_name = change_names["first_name"]
    auth.last_name = change_names["last_name"]


    response = auth._client.put(
        "/".join([API_URL, "changedetails", "changenames"]),
        json=change_names
    )

    assert response._status_code == 200

    response = auth._client.get(
        "/".join([API_URL, "user", "info"])  # trailing empty space is to get around 308 error
    )

    assert response._status_code == 200
    assert response.get_json()["first_name"] == auth.first_name
    assert response.get_json()["last_name"] == auth.last_name
    assert response.get_json()["email"] == auth.email


def test_user_balance(auth, ):
    auth.sign_up()
    auth.login()

    response = auth._client.get(
        "/".join([API_URL, "balance", "user", ""])  # trailing empty space is to get around 308 error
    )

    assert response._status_code == 200
    assert response.get_json()["balance"] == 100000.0

