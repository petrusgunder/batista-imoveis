from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import db, ADM, Usuario

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    tipo, id_real = user_id.split('-')
    if tipo == 'admin':
        return ADM.query.get(int(id_real))
    return Usuario.query.get(int(id_real))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.routes.public import public_bp
    app.register_blueprint(public_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app