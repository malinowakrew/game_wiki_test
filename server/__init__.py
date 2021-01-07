from flask import Flask, jsonify, request, redirect, url_for

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies,
)
from flask_mongoengine import MongoEngine

from src.game_creator.questions_creator import *
from src.game_creator.ranking import Ranking


app = Flask(__name__)

app.config['JWT_TOKEN_LOCATION'] = ['cookies']

#app.config['JWT_ACCESS_COOKIE_PATH'] = '/users/wikitest'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_CSRF_CHECK_FORM'] = True

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'wiki_test'


app.config['MONGODB_SETTINGS'] = {
    'db': 'wiki',
    'host': 'mongodb://localhost/wiki'
}

db = MongoEngine(app)

from . import (users, game)

app.register_blueprint(users.users)
app.register_blueprint(game.bp)
app.register_error_handler(400, game.handle_bad_request)

if __name__ == '__main__':
    disconnect()
    app.run(db)
