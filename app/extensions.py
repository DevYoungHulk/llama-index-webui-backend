from flask_login import LoginManager
from .models.types import User
from flask_jwt_extended import JWTManager

login_manager = LoginManager()
login_manager.login_view = 'login'
jwt_manager = JWTManager()


def config_extensions(app):
    login_manager.init_app(app)
    jwt_manager.init_app(app)
