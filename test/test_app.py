import pytest
from app import *
#from flask_mongoengine import MongoEngine


@pytest.fixture(name="client")
def client():
    app.testing = True
    app.config["USERNAME"] = "test"
    app.config["PASSWORD"] = "test"
    client = app.test_client()
    disconnect()
    #connect('wiki-test', host='mongodb://localhost/wiki-test')

    yield client


@pytest.fixture(name="client_jwt")
def client_jwt():
    app.testing = True
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_TOKEN_LOCATION'] = 'json'
    app.config['SERVER_NAME'] = 'localhost'
    app.config["USERNAME"] = "test"
    app.config["PASSWORD"] = "test"
    disconnect()
    #connect('wiki-test', host='mongodb://localhost/wiki-test')
    client = app.test_client()
    yield client

@pytest.fixture
def headers(client_jwt):
    name = {
        "username": app.config["USERNAME"]
    }
    with app.app_context():
        access_token = create_access_token(name)
        headers = {
            'access_token': access_token
        }
    return headers

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
    name = {
        "username": app.config["USERNAME"]
    }
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


def test_question_ident(client_jwt, headers):
    response = client_jwt.get('/wikitest/answer/1/B', json=headers)
    assert response.status_code == 200


def test_check_post(client):
    with app.app_context():
        answer = {
            'number': 1,
            'answer': "B"
        }
        response = client.post('/wikitest/answer', json=answer, follow_redirects=False)
    assert response.status_code == 302


def questions_validation_for_one_iteration(client_jwt, headers, number):
    return client_jwt.get('/wikitest/post/'+str(number), json=headers)


@pytest.mark.slow
def test_show_post(client_jwt, headers):
    for nr in range(0, 5):
        response = questions_validation_for_one_iteration(client_jwt, headers, nr)

        assert response.status_code == 200
        keys = ["question", "A", "B", "C"]
        for key in keys:
            assert key in response.json.keys()

        assert isinstance(response.json["question"], str)
        assert isinstance(response.json["A"], int)

    response = questions_validation_for_one_iteration(client_jwt, headers, 5)
    assert response.status_code == 401
    response = questions_validation_for_one_iteration(client_jwt, headers, 17)
    assert response.status_code == 401


