from flask import Flask
from config import Config
from app.models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes.public import public_bp
    app.register_blueprint(public_bp)

    return app
