import os
import logging
from flask import Flask
from flasgger import Swagger, swag_from
from bankAPI.config.swagger import template, swagger_config
from bankAPI.app import bank
from bankAPI.auth import auth


def create_app(test_config=None):
    logging.basicConfig(level=logging.DEBUG)
    # create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_mapping(
            SWAGGER={
                'title': "Bank API",
                'uiversion': 3
            }
        )

    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(bank)
    app.register_blueprint(auth)

    Swagger(app, config=swagger_config, template=template)

    @app.route("/test")
    @swag_from("./docs/test_doc.yaml")
    def hello_test():
        return "Hello, World"

    # # homepage
    # @app.route("/")
    # @swag_from("./docs/auth/login.yaml")
    # def homepage():
    #     return "Banking API"

    return app
