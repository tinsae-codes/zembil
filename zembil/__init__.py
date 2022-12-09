from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from zembil.config import Config


db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()


def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    db.init_app(app)

    return app
