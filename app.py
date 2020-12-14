"""
from flask import Flask
from flask import Flask, jsonify, abort, request, make_response, render_template
from db.schema import *

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

@app.route('/')
def hello_world():
    user = test()
    try:
        users = user.to_mongo().to_dict()
        print(users)
        users['_id'] = "123"
        return jsonify(users)
    except Exception as e:
        print(e)
        return "Pies"


@app.route('/task', methods=['GET'])
def get_tasks():
    return jsonify(tasks[0])


if __name__ == '__main__':
    app.run()
"""
from datetime import timedelta
from flask import Flask, jsonify, request, redirect, url_for

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies,
)

from db.schema import *

from src.game_creator.questions_creator import *

app = Flask(__name__)

app.config['JWT_TOKEN_LOCATION'] = ['cookies']

app.config['JWT_ACCESS_COOKIE_PATH'] = '/wikitest/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

app.config['JWT_COOKIE_CSRF_PROTECT'] = True

app.config['JWT_SECRET_KEY'] = 'wiki_test'


jwt = JWTManager(app)




@app.route('/token/auth', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    try:
        # user = User.query.filter_by(email=form.email.data).first()
        user = Account.objects(name=username)[0]

    except Exception as error:
        return jsonify({'login': False}), 401

    if not (argon2.verify(password, user.passwd)):
        return jsonify({'login': False}), 401

    # Create the tokens we will be sending back to the user
    time_limit = timedelta(minutes=30)  # set limit for user
    access_token = create_access_token(identity=username, expires_delta=time_limit)
    refresh_token = create_refresh_token(identity=username)

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
    timeLimit = timedelta(minutes=30)
    access_token = create_access_token(identity=current_user, expires_delta=timeLimit)

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
    return jsonify(data), 201


@app.route('/wikitest/redirect', methods=['POST', 'GET'])
def redirection():
    ok = request.json.get('ok', True)
    if ok:
        return redirect(url_for('scrap'), code=302)
    else:
        return jsonify({"redirected": False}), 401


"""
@app.route('/nic', methods=['GET'])
def hello_world():
    user = test()
    try:
        users = user.to_mongo().to_dict()
        print(users)
        users['_id'] = "123"
        return jsonify(users)
    except Exception as e:
        print(e)
        return "Pies"
"""

if __name__ == '__main__':
    app.run()
