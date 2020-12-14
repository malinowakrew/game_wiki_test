import pytest

import app
import os
from flask import Flask

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

@pytest.fixture
def client():
    app = create_app()
    return app

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='Ed', password='123'):
        return self._client.post(
            '/auth/login',
            data={"username": username,
                    "password": password}
        )


def test_auth(client):
    to = AuthActions(client)
    to = to.login()
    assert to == {"login": True}