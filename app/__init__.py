import json

from flasgger import Swagger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_cors import CORS

db = SQLAlchemy()
api = Api()


def create_app(config):
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SWAGGER'] = {
        'openapi': '3.0.2'
    }

    swagger_config = json.loads(open('app/swagger_config.json').read())
    template = json.loads(open('app/swagger_template.json').read())
    Swagger(app, config=swagger_config, template=template)
    db.init_app(app)
    api.app = app
    return app
