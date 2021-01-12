from test import *
from test.test_page_scraping import random_date


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


def answer_for_one_iteration(client_jwt, headers, number, answer_letter):
    return client_jwt.get('game/answer/{}/{}'.format(number, answer_letter), json=headers)


def test_check_user_answer(client_jwt, headers):
    for number in range(0, 5):

        for answer_letter in ["A", "B", "C"]:
            response = answer_for_one_iteration(client_jwt, headers, number, answer_letter)
            assert response.status_code == 200

            for key_name in response.json.keys():
                assert key_name in ["point", "next-page", "correct"]

            if len(response.json) == 2:
                assert response.json["point"] == 1
            else:
                assert response.json["point"] == 0


def questions_validation_for_one_iteration(client_jwt, headers, number):
    return client_jwt.get('game/question/'+str(number), json=headers)


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


def top_users_for_verify_user(verify_client_jwt, verify_headers, date):
    response_not_follow = verify_client_jwt.post("/users/top-users", json=date, follow_redirects=False)
    assert response_not_follow.status_code == 302

    response_follow = verify_client_jwt.get("/users/top-users/"+date["date"], json=verify_headers)
    assert response_follow.status_code == 200

    for key_name in response_follow.json.keys():
        assert key_name in ["date", "users_scores"]


def top_users_for_not_verify_user(client_jwt, headers, date):
    response_not_follow = client_jwt.post("/users/top-users", json=date, follow_redirects=False)
    assert response_not_follow.status_code == 302

    response_follow = client_jwt.get("/users/top-users/"+date["date"], json=headers)
    assert response_follow.status_code == 403

    for key_name in response_follow.json.keys():
        assert key_name in ["error-type", "route", "text"]


def test_top_users(verify_client_jwt, verify_headers, client_jwt, headers):
    for i in range(0, 5):
        day = random_date().strftime("%d-%m-%Y")
        date = {"date": day}

        top_users_for_verify_user(verify_client_jwt, verify_headers, date)
        top_users_for_not_verify_user(client_jwt, headers, date)


def test_show_games_ranking(client_jwt, headers):
    response = client_jwt.get("/users/ranking", json=headers)
    assert response.status_code == 200

    for key_name in response.json.keys():
        day = datetime.strptime(key_name, '%d-%m-%Y')
        assert isinstance(day, datetime)
        for key in response.json[key_name].keys():
            assert key in ["questions", "points"]
            assert key not in ["nic", "pieski", "password"]


# def test_suite_client(client):
#     test_login(client)
#     test_login_not(client)
#
#
# def test_suite_jwt(client_jwt, headers, verify_client_jwt, verify_headers, client):
#     test_show_games_ranking(client_jwt, headers)
#     test_test(client_jwt, headers)
#     test_check_user_answer(client_jwt, headers)
#     test_show_question(client_jwt, headers)
#     test_show_games_ranking(client_jwt, headers)
#
#     test_top_users(verify_client_jwt, verify_headers, client_jwt, headers)

