from flask_login import LoginManager

login_manager = LoginManager()


# 初始化拓展
def config_extensions(app):

    login_manager.init_app(app)
    