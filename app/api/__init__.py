from .indexApi import index
from .fileApi import file
from .chatApi import chat

DEFAULT_BLUEPRINT = [
    (index, '/api/index'),
    (file, '/api/file'),
    (chat, '/api/chat')
]


def config_blueprint(app):
    for blueprint, prefix in DEFAULT_BLUEPRINT:
        print('prefix = '+prefix)
        app.register_blueprint(blueprint, url_prefix=prefix)
