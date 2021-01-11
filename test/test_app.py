from test import *

# @pytest.fixture(name="client")
# def client():
#     app.testing = True
#     app.config["USERNAME"] = "Wojtus123"
#     app.config["PASSWORD"] = "13"
#     client = app.test_client()
#     disconnect()
#     connect('wiki', host='mongodb://localhost/wiki')
#
#     yield client
#
#
# @pytest.fixture(name="client_jwt")
# def client_jwt():
#     app.testing = True
#     app.config['JWT_COOKIE_CSRF_PROTECT'] = False
#     app.config['JWT_TOKEN_LOCATION'] = 'json'
#     app.config['SERVER_NAME'] = 'localhost'
#     app.config["USERNAME"] = "Wojtus123"
#     app.config["ROLE"] = "user"
#     app.config["PASSWORD"] = "13"
#     disconnect()
#     connect('wiki', host='mongodb://localhost/wiki')
#     client = app.test_client()
#     yield client
#
# @pytest.fixture
# def headers(client_jwt):
#     name = {
#         "username": app.config["USERNAME"],
#         "role": app.config["ROLE"]
#     }
#     with app.app_context():
#         access_token = create_access_token(name)
#         headers = {
#             'access_token': access_token
#         }
#     return headers
#


def test_login(client):
    log = {"username": app.config["USERNAME"], "password": app.config["PASSWORD"]}
    response = client.post('users/token/auth', json=log)
    assert response.status_code == 200
    assert response.json['login']


def test_login_not(client):
    log = {"username": "Pieski", "password": "13"}
    response = client.post('users/token/auth', json=log)
    assert response.status_code == 401
    assert not response.json['login']


def test_scrap(client_jwt, headers):
    with app.app_context():
        response = client_jwt.get('game/scraper', json=headers)
    assert response.status_code == 200


def test_welcome(client_jwt, headers):
    response = client_jwt.get('/users/example', json=headers)
    assert response.status_code == 200


def test_test(client_jwt, headers):
    response_get = client_jwt.get('/game/test/0', follow_redirects=False)
    assert response_get.status_code == 302

    with app.app_context():
        answer = {
            'answer': "B"
        }
    response_post = client_jwt.post('/game/test/0', json=answer, follow_redirects=False)
    assert response_post.status_code == 302


def test_answer_for_one_iteration(client_jwt, headers, number, answer_letter):
    return client_jwt.get('game/answer/{}/{}'.format(number, answer_letter), json=headers)


def test_check_user_answer(client_jwt, headers):
    for number in range(0, 5):

        for answer_letter in ["A", "B", "C"]:
            response = test_answer_for_one_iteration(client_jwt, headers, number, answer_letter)
            assert response.status_code == 200

            for key_name in response.json.keys():
                assert key_name in ["point", "next-page", "correct"]

            if len(response.json) == 2:
                assert response.json["point"] == 1
            else:
                assert response.json["point"] == 0


def questions_validation_for_one_iteration(client_jwt, headers, number):
    return client_jwt.get('game/question/'+str(number), json=headers)


@pytest.mark.slow
def test_show_question(client_jwt, headers):
    for nr in range(0, 5):
        response = questions_validation_for_one_iteration(client_jwt, headers, nr)

        assert response.status_code == 200
        keys = ["question", "A", "B", "C"]
        for key in keys:
            assert key in (response.json["question"]).keys()

        assert isinstance(response.json["question"]["question"], str)
        assert isinstance(response.json["question"]["A"], int)
        assert isinstance(response.json["question"]["B"], int)
        assert isinstance(response.json["question"]["C"], int)

        for key_name in response.json.keys():
            assert key_name in ["question", "next-page"]

    response = questions_validation_for_one_iteration(client_jwt, headers, 5)
    assert response.status_code == 404
    response = questions_validation_for_one_iteration(client_jwt, headers, 17)
    assert response.status_code == 404


def test_top_users_for_verify_user(verify_client_jwt, verify_headers):
    response = verify_client_jwt.get("/users/top-users", json=verify_headers)
    assert response.status_code == 200


def test_top_users_for_not_verify_user(client_jwt, headers):
    response = client_jwt.get("/users/top-users", json=headers)
    assert response.status_code == 403


def test_top_users(verify_client_jwt, verify_headers, client_jwt, headers):
    test_top_users_for_verify_user(verify_client_jwt, verify_headers)
    test_top_users_for_not_verify_user(client_jwt, headers)

