from random import choices
from string import ascii_letters, digits

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

header = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}

generator_base = ascii_letters + digits

username = "".join(choices(generator_base, k=10))
password = "".join(choices(generator_base, k=10))


def test_invalid_token_login():
    # Data argument is for form input
    data = f"username={username}&password={password}"
    response = client.post("/token", data=data, headers=header)

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect user name or password"}


def test_register():
    body = {
        "username": username,
        "password": password,
    }

    response = client.post("/register", json=body)

    assert response.status_code
    assert response.json()


def test_valid_token_login():
    # Data argument is for form input
    data = f"username={username}&password={password}"
    response = client.post("/token", data=data, headers=header)

    assert response.status_code == 200
    assert response.json()["access_token"]
