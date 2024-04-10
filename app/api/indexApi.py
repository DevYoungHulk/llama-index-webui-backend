from flask import Blueprint, request
import logging
from app.services.index_mangement import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.celery_tasks.indexJob import *
index = Blueprint('index', __name__)
logger = logging.getLogger('root')


@index.route('/<group_id>/<file_id>', methods=['POST'])
@jwt_required()
def add_index_for_file(group_id, file_id):
    indexed, msg = isIndexed(group_id, file_id)
    if msg:
        return {'msg': msg}, 404
    elif indexed:
        return {'msg': 'already indexed'}
    else:
        locked, msg = islockedFile(group_id, file_id)
        if locked:
            return {'msg': msg}
        else:
            # create_index_task.delay(user_id, file_id)
            # return {'msg': 'start indexing'}
            return add_index_safe(group_id, file_id)


@index.route('/<group_id>/<file_id>', methods=['DELETE'])
@jwt_required()
def remove(file_id):
    user_id = get_jwt_identity()
    return remove_index(user_id, file_id)

# 添加confuluence loader 配置，API参数：{base_url, api_token}


# @index.route('/loader/config', methods=['POST'])
# @jwt_required()
# def config_loader():
#     user_id = get_jwt_identity()
#     return add_confluence_loader_conf(user_id=user_id, json=request.json).to_dict()


@index.route('/<group_id>/<file_id>/documents', methods=['POST'])
@jwt_required()
def load_documents(group_id, file_id):
    file = BaseFile.objects(group_id=group_id, id=file_id).first()
    if file:
        data = []
        doc: Document
        for doc in loadDoc(file=file):
            data.append(json.loads(doc.to_json()))
        return {'data': data}
    else:
        return {'msg': 'file not found'}, 404


@index.route('/<group_id>/<file_id>/nodes', methods=['POST'])
@jwt_required()
def load_nodes(group_id, file_id):
    file = BaseFile.objects(group_id=group_id, id=file_id).first()
    if file:
        data = []
        node: BaseNode
        for node in loadNodes(file=file):
            data.append(node.to_dict())
        return {'data': data}
    else:
        return {'msg': 'file not found'}, 404
