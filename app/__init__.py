from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask.json import jsonify
from app.api import config_blueprint
from app.extensions import config_extensions
from .config import config
from bson import json_util
import json
from .log import setup_custom_logger
from mongoengine import connect
from datetime import date, datetime

logger = setup_custom_logger('root')
logger.info('logger inited')
 
    
# class ModelProvider(DefaultJSONProvider):

#     @staticmethod
#     def default(obj):
#         return json.loads(json_util.dumps(obj))


def creat_app(DevelopmentConfig):

    # 实例化 app
    app = Flask(__name__)
    # app.json = ModelProvider(app)
    # 加载配置项
    app.config.from_object(config.get(DevelopmentConfig))

    connect(host=app.config['MONGO_URI'], alias='default')

    # 加载拓展
    config_extensions(app)

    # 加载蓝图
    config_blueprint(app)

    return app
