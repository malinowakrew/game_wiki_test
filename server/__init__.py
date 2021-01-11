from flask import Flask, send_from_directory, jsonify #request, redirect, url_for,

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies,
)
from flask_mongoengine import MongoEngine

from src.game_creator.questions_creator import *
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.exceptions import NotFound, MethodNotAllowed, InternalServerError

app = Flask(__name__)

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
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

@app.route('/static8/<path:path>')
def send_static(path):
    return send_from_directory('static8', path)


SWAGGER_URL = '/swagger'
API_URL = '/static8/swagger.json'
swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "wiki"
    }
)
app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)


@app.route('/', methods=['GET'])
def welcome():
    return "Hejka naklejka"


@app.errorhandler(NotFound)
def handle_bad_request(error):
    return jsonify({"route": False,
                    "error-type": "Not Found",
                    "text": str(error)}), 404


@app.errorhandler(MethodNotAllowed)
def handle_bad_request(error):
    return jsonify({"route": False,
                    "error-type": "Method Not Allowed",
                    "text": str(error)}), 405


@app.errorhandler(InternalServerError)
def handle_bad_request(error):
    return jsonify({"route": False,
                    "error-type": "Internal Server Error",
                    "text": str(error)}), 500


@app.errorhandler(ValueError)
def handle_bad_request(error):
    return jsonify({"route": False,
                    "error-type": "Value Error",
                    "text": str(error)}), 400


if __name__ == '__main__':
    disconnect()
    app.run(db, debug=True)


