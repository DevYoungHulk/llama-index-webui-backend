from flask import Blueprint, request
import logging
from app.services.index_mangement import *
from flask_jwt_extended import jwt_required, get_jwt_identity
# from app.celery_tasks.indexJob import *
index = Blueprint('index', __name__)
logger = logging.getLogger('root')


@index.route('/create/<file_id>', methods=['POST'])
@jwt_required()
def add_index_for_file(file_id):
    user_id = get_jwt_identity()
    locked, msg = islockedFile(user_id, file_id)
    if locked:
        return {'msg': msg}
    # create_index_task.delay(user_id, file_id)
    # return {'msg': 'indexing'}
    try:
        return add_index(user_id, file_id)
    except Exception as e:
        unlockFile(user_id, file_id)
        logger.error(e)
        return {'msg': 'indexing failed'}, 500


@index.route('/remove/<file_id>', methods=['DELETE'])
@jwt_required()
def remove(file_id):
    user_id = get_jwt_identity()
    return remove_index(user_id, file_id)

# 添加confuluence loader 配置，API参数：{base_url, api_token}


@index.route('/loader/config', methods=['POST'])
@jwt_required()
def config_loader():
    user_id = get_jwt_identity()
    return add_confluence_loader_conf(user_id=user_id, json=request.json).to_dict()
