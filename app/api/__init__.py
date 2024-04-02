from .indexApi import index
from .docApi import doc
from .groupApi import chat_group
from.chatApi import chat
from .userApi import user
import logging
logger = logging.getLogger('root')

DEFAULT_BLUEPRINT = [
    (index, '/api/index'),
    (doc, '/api/doc'),
    (chat_group, '/api/group'),
    (chat, '/api/chat'),
    (user, '/api/user')
]


def config_blueprint(app):
    for blueprint, prefix in DEFAULT_BLUEPRINT:
        logger.info('prefix = '+prefix)
        app.register_blueprint(blueprint, url_prefix=prefix)
