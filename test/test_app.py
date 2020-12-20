import pytest
from app import *
from mongoengine import connect


@pytest.fixture
def client():
    app.testing = True
    app.config["USERNAME"] = "Ed"
    app.config["PASSWORD"] = "123"
    client = app.test_client()
    connect('wiki', host='mongodb://localhost/wiki')
    yield client


@pytest.fixture
def client_jwt():
    app.testing = True
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_TOKEN_LOCATION'] = 'json'
    app.config["USERNAME"] = "Ed"
    app.config["PASSWORD"] = "123"
    client = app.test_client()
    connect('wiki', host='mongodb://localhost/wiki')
    yield client


def test_login(client):
    log = {"username": app.config["USERNAME"], "password": app.config["PASSWORD"]}
    response = client.post('/token/auth', json=log)
    assert response.status_code == 200
    assert response.json['login']


def test_login_not(client):
    log = {"username": "Pieski", "password": "13"}
    response = client.post('/token/auth', json=log)
    assert response.status_code == 401
    assert not response.json['login']


def test_scrap(client_jwt):
    name = app.config["USERNAME"]
    with app.app_context():
        access_token = create_access_token(name)
        headers = {
            'access_token': access_token
        }
    response = client_jwt.get('/wikitest/scrap', json=headers)
    assert response.status_code == 200


def test_welcome(client_jwt):
    name = {
        "username": app.config["USERNAME"]
    }
    with app.app_context():
        access_token = create_access_token(name)
        headers = {
            'access_token': access_token
        }
    response = client_jwt.get('/wikitest/example', json=headers)
    assert response.status_code == 200
    assert response.json['hello'] == f"from {name}"


def test_question_ident():
    assert True
