from .indexApi import index
from .fileApi import file
from .chatApi import chat
from .userApi import user

DEFAULT_BLUEPRINT = [
    (index, '/api/index'),
    (file, '/api/file'),
    (chat, '/api/chat'),
    (user, '/api/user')
]


def config_blueprint(app):
    for blueprint, prefix in DEFAULT_BLUEPRINT:
        print('prefix = '+prefix)
        app.register_blueprint(blueprint, url_prefix=prefix)
