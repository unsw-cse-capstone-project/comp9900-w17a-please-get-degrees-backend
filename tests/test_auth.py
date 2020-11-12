import pytest
from tests.conftest import API_URL


@pytest.mark.parametrize(("email", "password", "message", "code"), (
        ("", "", "Email is required", 422),
        ("a", "", "Password should be at least 8 characters", 411),
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
    assert response.get_json()["message"] == message
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
    assert response.get_json()["message"] == "New user created!"

    response = client.post(
        "/".join([API_URL, "signup"]),
        data=new_user
    )
    assert response.get_json()["message"] == "User already exists"
    assert response._status_code == 403


@pytest.mark.parametrize(("email", "password", "message", "code"), (
        ("test@test.com", "pass1234", "Login successful", 200),
        ("test@test.com", "WrongPassword", "Incorrect password, retry", 401),
        ("test_doesnt_exist@test.com", "pass1234", "User not found", 404),
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

    assert response.get_json()["message"] == message
    assert response._status_code == code


def test_logout(auth):
    auth.sign_up()
    auth.login()
    auth.logout()

    response = auth._client.get(
        "/".join([API_URL, "user", "info"]),
    )

    assert response._status_code == 401


