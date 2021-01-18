from flask import Flask, send_from_directory, jsonify

from flask_jwt_extended import (
    JWTManager
)
from flask_mongoengine import MongoEngine


from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.exceptions import NotFound, MethodNotAllowed, InternalServerError, Gone

app = Flask(__name__)

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# app.config['JWT_REFRESH_COOKIE_PATH'] = 'users/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_CSRF_CHECK_FORM'] = False

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'wiki_test'

app.config['MONGODB_SETTINGS'] = {
    'db': 'wiki',
    'host': 'mongodb://localhost/wiki'
}

db = MongoEngine(app)

from . import (users, game)

app.register_blueprint(users.accounts)
app.register_blueprint(game.bp)

@app.route('/static17/<path:path>')
def send_static(path):
    return send_from_directory('static17', path)


SWAGGER_URL = '/swagger'
API_URL = '/static17/swagger.json'
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

@app.errorhandler(Gone)
def handle_bad_request(error):
    return jsonify({"route": False,
                    "error-type": "Gone",
                    "text": str(error)}), 410


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


@app.errorhandler(Exception)
def handle_bad_request(error):
    return jsonify({"route": False,
                    "error-type": "Unknown error",
                    "text": str(error)}), 401

# @app.after_request
# @jwt_refresh_token_required
# def refresh(response):
#     current_user = get_jwt_identity()
#     time_limit = timedelta(hours=2)
#     access_token = create_access_token(identity=current_user, expires_delta=time_limit, fresh=False)
#
#     set_access_cookies(response, access_token)
#     return response


if __name__ == '__main__':
    app.run(db, debug=True)


