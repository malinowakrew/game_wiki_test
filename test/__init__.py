"""
with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('profile', username='John Doe'))
"""
import pytest
from server import *

@pytest.fixture(name="client")
def client():
    app.testing = True
    app.config["USERNAME"] = "Wojtus123"
    app.config["PASSWORD"] = "13"
    client = app.test_client()
    disconnect()
    connect('wiki', host='mongodb://localhost/wiki')

    yield client


@pytest.fixture(name="client_jwt")
def client_jwt():
    app.testing = True
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_TOKEN_LOCATION'] = 'json'
    app.config['SERVER_NAME'] = 'localhost'
    app.config["USERNAME"] = "Wojtus"
    app.config["ROLE"] = "user"
    app.config["PASSWORD"] = "13"
    disconnect()
    connect('wiki', host='mongodb://localhost/wiki')
    client = app.test_client()
    yield client

@pytest.fixture(name="verify_client_jwt")
def verify_client_jwt():
    app.testing = True
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_TOKEN_LOCATION'] = 'json'
    app.config['SERVER_NAME'] = 'localhost'
    app.config["USERNAME"] = "Wojtus123"
    app.config["ROLE"] = "verify-user"
    app.config["PASSWORD"] = "13"
    disconnect()
    connect('wiki', host='mongodb://localhost/wiki')
    client = app.test_client()
    yield client

@pytest.fixture
def headers(client_jwt):
    name = {
        "username": app.config["USERNAME"],
        "role": app.config["ROLE"]
    }
    with app.app_context():
        access_token = create_access_token(name)
        headers = {
            'access_token': access_token
        }
    return headers

@pytest.fixture
def verify_headers(verify_client_jwt):
    name = {
        "username": app.config["USERNAME"],
        "role": app.config["ROLE"]
    }
    with app.app_context():
        access_token = create_access_token(name)
        headers = {
            'access_token': access_token
        }
    return headers

