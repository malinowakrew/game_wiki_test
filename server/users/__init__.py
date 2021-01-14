from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies,
)
from flask import jsonify, request, redirect, url_for, Blueprint

from werkzeug.exceptions import Forbidden, Unauthorized
from datetime import timedelta
from db.schema import *
from src.game_creator.ranking import Ranking

from mongoengine import NotUniqueError


accounts = Blueprint('accounts', __name__, url_prefix='/accounts')


@accounts.route('/example', methods=['GET'])
@jwt_required
def welcome():
    username = get_jwt_identity()
    return jsonify({'hello': 'from {}'.format(username)}), 200


@accounts.route('/ranking/<name>', methods=['GET'])
@jwt_required
def show_games_ranking(name):
    current_user = get_jwt_identity()["username"]
    if name == current_user:
        ranking = Ranking(current_user)
        return ranking.read_user_answers_from_games(), 200
    else:
        raise Unauthorized


@accounts.route('/top-users/<day>', methods=['GET'])
@jwt_required
def top_users_for_day(day):
    if get_jwt_identity()['role'] == "verify-user":
        other_users_scores = {}
        accounts = Account.objects(email__exists=True)
        for account in accounts:
            games = account.score
            for game in games:
                if game.date.strftime("%d-%m-%Y") == day:
                    other_users_scores[account.name] = game.points
        return {
            "users_scores": other_users_scores,
            "date": day
               }, 200
    else:
        raise Forbidden


@accounts.route('/top-users', methods=['POST'])
def top_users():
    try:
        date = request.json.get('date', None)
        date = datetime.strptime(date, '%d-%m-%Y')

    except AttributeError:
        date = datetime.now()

    day = datetime.strftime(date, '%d-%m-%Y')
    return redirect(url_for("users.top_users_for_day", day=day), code=302)


@accounts.route('/<name>', methods=['DELETE'])
@jwt_required
def delete_account(name):
    print(name)
    user = get_jwt_identity()["username"]
    if user == name:
        user_account_in_db = Account.objects(name=user)[0]
        user_account_in_db.delete()
        resp = jsonify({"route": True,
                        "msg": "Account was deleted"})
        unset_jwt_cookies(resp)
        return resp, 200
    else:
        raise Unauthorized


@accounts.route('/auth', methods=['POST'])
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
    time_limit = timedelta(minutes=10)  # set limit for user
    access_token = create_access_token(identity={"username": user.name,
                                                 "role": user.role}, expires_delta=time_limit, fresh=True)
    time_limit = timedelta(hours=2)
    refresh_token = create_refresh_token(identity={"username": user.name,
                                                   "role": user.role}, expires_delta=time_limit)

    # Set the JWT cookies in the response
    resp = jsonify({'login': True,
                    'next-page': url_for("game.start_game")})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200


@accounts.route('/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


@accounts.route('/', methods=['POST'])
def create_account():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    email = request.json.get('email', None)

    if email:
        user_role = role[0]
    else:
        user_role = role[1]

    try:
        user = Account(role=user_role, name=username, email=email)
        user.passwd = password
        user.save(cascade=True)
        return user.user_view()
    except NotUniqueError as error:
        return {"account-created": False,
                "error": str(error),
                "description": "User name not unique"}, 200


@accounts.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    time_limit = timedelta(hours=10)
    access_token = create_access_token(identity=current_user, expires_delta=time_limit, fresh=False)
    time_limit = timedelta(hours=2)
    refresh_token = create_refresh_token(identity=current_user, expires_delta=time_limit)

    response = jsonify({"refresh": True})
    set_refresh_cookies(response, refresh_token)
    set_access_cookies(response, access_token)
    return response


@accounts.errorhandler(Forbidden)
def handle_forbidden(error):
    return jsonify({"route": False,
                    "error-type": "Forbidden entrance",
                    "text": str(error)}), 403


