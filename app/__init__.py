from flask import Flask

from app.api import config_blueprint
from app.extensions import config_extensions
from .config import config
from bson import json_util
from .log import setup_custom_logger
from mongoengine import connect
from werkzeug.exceptions import NotFound
from celery import Celery
from flask import request, g, jsonify
from flask_cors import CORS
import uuid
import traceback

logger = setup_custom_logger('root')
logger.info('logger inited')


def create_app(config_name):

    # 实例化 app
    app = Flask(__name__)
    # 给app定义一个Json序列化工具，可以支持mongodb中的datetime和date类型到ISO字符串格式的转换
    app.json_encoder = json_util.default

    # 给app添加配置，用于全局try catch,在捕获异常的时候返回一个json格式的错误信息

    # 加载配置项
    app.config.from_object(config.get(config_name))
    # print('--------__name__--------')
    # print(__name__)
    # celery_app = Celery(__name__, broker='redis://127.0.0.1:6379/0',
    #                     backend='redis://127.0.0.1:6379/0')
    # # celery_app.config_from_object('app.celery_tasks.celeryconfig')
    # celery_app.set_current()

    try:
        # 连接MongoDB，使用异常处理避免应用崩溃
        logger.info(app.config['MONGO_URI'])
        connect(host=app.config['MONGO_URI'],
                db=app.config['MONGO_DB_NAME'],
                username=app.config['MONGO_USERNAME'],
                password=app.config['MONGO_PASSWORD'],
                alias='default')
    except Exception as e:
        # 在实际应用中，应记录日志或发送报警
        logger.info(f"MongoDB连接失败: {e}")
        raise
    try:
        config_extensions(app)
        config_blueprint(app)
    except NotFound:
        # 这里举例处理找不到蓝图或扩展的情况
        logger.error("加载蓝图或扩展失败，确保它们已正确定义")
        raise

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.before_request
    def log_request_info():
        g.request_id = str(uuid.uuid4())
        logger.debug('(%s) Request Headers: %s', g.request_id, request.headers)
        logger.info('(%s) Request Body: %s', g.request_id, request.get_data())

    @app.after_request
    def log_response_info(response):
        logger.debug('(%s) Response Headers: %s',
                     g.request_id, response.headers)
        logger.info('(%s) Response Body: %s',
                    g.request_id, response.get_data())
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        traceback_text = traceback.format_exc()
        error_message = {'msg': str(e)}
        logger.error(error_message)
        logger.error(traceback_text)
        response = jsonify(error_message)
        response.status_code = 500 if isinstance(e, Exception) else 400
        return response
    return app
