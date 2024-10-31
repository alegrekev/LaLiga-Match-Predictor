from flask import Flask
from flask_cors import CORS

from .extensions import api, db
from .resources import ns

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    api.init_app(app)
    db.init_app(app)

    api.add_namespace(ns)

    with app.app_context():
        db.create_all()

    return app