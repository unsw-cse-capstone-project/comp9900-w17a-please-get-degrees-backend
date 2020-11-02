import pytest
from tests.conftest import API_URL
from flask import g, session
from simvestr.models import db


def test_register(client, app):
    new_user = {
      "email_id": "test@testmail.com",
      "password": "pass1234",
      "first_name": "test",
      "last_name": "register"
    }
    response = client.post(
        "/".join([API_URL, "signup"]), data=new_user
    )
    assert response._status_code == 200




@pytest.mark.parametrize(('email', 'password', 'message'), (
    ("", "", "Email is required"),
    ("a", "", "Password should be at least 8 characters"),
    ("test@testmail.com", "pass1234", "New user created!"),
    ("test@testmail.com", "pass1234", "Already exists"),
))
def test_register_validate_input(client, email, password, message):

    new_user = {
        "email_id": email,
        "password": password,
        "first_name": "test",
        "last_name": "register"
    }
    response = client.post(
        "/".join([API_URL, "signup"]),
        data=new_user
    )
    assert message == response.get_json()["message"]