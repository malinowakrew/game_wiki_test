from datetime import timedelta
from flask import Flask, jsonify, request, redirect, url_for

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies,
)
from flask_mongoengine import MongoEngine

"""
from db.schema import *
from authenticate import token_required
from flask_wtf.csrf import CSRFProtect
"""

from src.game_creator.questions_creator import *

app = Flask(__name__)
"""
db = MongoEngine(app)
app.config['MONGODB_SETTINGS'] = {
    'db': 'wiki',
    'host': 'mongodb://localhost/wiki'
}
"""

app.config['JWT_TOKEN_LOCATION'] = ['cookies']

app.config['JWT_ACCESS_COOKIE_PATH'] = '/wikitest/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_CSRF_CHECK_FORM'] = True

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'wiki_test'

#tak nie wolno raczej robić
#app.secret_key = "super secret key"
#csrf = CSRFProtect(app)

@app.route('/token/auth', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    try:
        user = Account.objects(name=username)[0]

    except Exception as error:
        return jsonify({'login': False}), 401

    if not (argon2.verify(password, user.passwd)):
        return jsonify({'login': False}), 401

    # Create the tokens we will be sending back to the user
    time_limit = timedelta(minutes=30)  # set limit for user
    access_token = create_access_token(identity=user.name, expires_delta=time_limit)
    refresh_token = create_refresh_token(identity=user.name)

    # Set the JWT cookies in the response
    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200


@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    time_limit = timedelta(minutes=30)
    access_token = create_access_token(identity=current_user, expires_delta=time_limit)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


@app.route('/token/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


@app.route('/wikitest/example', methods=['GET'])
@jwt_required
def welcome():
    username = get_jwt_identity()
    return jsonify({'hello': 'from {}'.format(username)}), 200


@app.route('/wikitest/scrap', methods=['GET'])
@jwt_required
def scrap():
    game_questions = QuestionCreator()
    game_questions.read()
    data = game_questions.dict_maker()
    current_user = get_jwt_identity()
    game_questions.add_game_to_user(data, current_user)
    return "ok"
    #return redirect(url_for('show_post', post_id=0), code=302)


@app.route('/wikitest/redirect', methods=['POST', 'GET'])
def redirection():
    ok = request.json.get('ok', True)
    if ok:
        return redirect(url_for('scrap'), code=302)
    else:
        return jsonify({"redirected": False}), 401


@app.route('/wikitest/post/<int:post_id>', methods=['GET', 'POST'])
@jwt_required
def show_post(post_id):
    if request.method == 'GET':
        game_questions = QuestionCreator()
        current_user = get_jwt_identity()
        quest = game_questions.user_question_reader(post_id, current_user)

        return quest.user_view(), 200


@app.route('/wikitest/answer/<int:number>/<answer>', methods=['GET', 'POST'])
@jwt_required
def question_ident(number, answer):
    current_user = get_jwt_identity()
    game_questions = QuestionCreator()
    quest = game_questions.user_question_reader(number, current_user)
    point = game_questions.check_answer(answer, quest, current_user)

    return jsonify({"points": point}), 200


@app.route('/wikitest/answer', methods=['POST'])
def check_post():
    answer = request.json.get("answer", None)
    number = request.json.get("number", None)
    return redirect(url_for("question_ident", number=number, answer=answer), code=302)

"""
@jwt.error_handler
def error_handler(error):
    return "Error: {}".format(error), 400

"""


if __name__ == '__main__':
    app.run()
