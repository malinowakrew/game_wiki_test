import pytest
from app import *
from mongoengine import connect


@pytest.fixture
def client():
    app.testing = True
    client = app.test_client()
    connect('wiki', host='mongodb://localhost/wiki')
    yield client

def test_login(client):
    log = {"username": "Ed", "password": "123"}
    response = client.post('/token/auth', json=log)
    assert response.status_code == 200
    assert response.json['login']

