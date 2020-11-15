import pytest
from tests.conftest import API_URL


@pytest.mark.parametrize(("email", "password", "message", "code"), (
        ("", "", "422 UNPROCESSABLE ENTITY", 422),
        ("a", "", "411 LENGTH REQUIRED", 411),
))
def test_register_validate_input(client, email, password, message, code):
    new_user = {
        "email": email,
        "password": password,
        "first_name": "test",
        "last_name": "register"
    }
    response = client.post(
        "/".join([API_URL, "signup"]),
        data=new_user
    )
    assert response._status == message
    assert response._status_code == code


def test_register(client, app):
    new_user = {
        "email": "test@test.com",
        "password": "pass1234",
        "first_name": "test",
        "last_name": "register"
    }
    response = client.post(
        "/".join([API_URL, "signup"]), data=new_user
    )
    assert response._status_code == 201


def test_user_signup(client):
    new_user = {
        "email": "test@testmail.com",
        "password": "pass1234",
        "first_name": "test",
        "last_name": "register"
    }
    response = client.post(
        "/".join([API_URL, "signup"]),
        data=new_user
    )
    assert response._status == "201 CREATED"

    response = client.post(
        "/".join([API_URL, "signup"]),
        data=new_user
    )
    assert response._status == "403 FORBIDDEN"
    assert response._status_code == 403


@pytest.mark.parametrize(("email", "password", "message", "code"), (
        ("test@test.com", "pass1234", "200 OK", 200),
        ("test@test.com", "WrongPassword", "401 UNAUTHORIZED", 401),
        ("test_doesnt_exist@test.com", "pass1234", "404 NOT FOUND", 404),
))
def test_login(client_new_user, email, password, message, code):
    user = {
        "email": email,
        "password": password,
    }
    response = client_new_user.post(
        "/".join([API_URL, "login"]),
        data=user
    )

    assert response._status == message
    assert response._status_code == code


def test_logout(auth):
    auth.sign_up()
    auth.login()
    auth.logout()

    response = auth._client.get(
        "/".join([API_URL, "user", "info"]),
    )

    assert response._status_code == 401


