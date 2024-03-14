from flask import Blueprint, request
import logging
from ..services.index_mangement import *
from flask_jwt_extended import jwt_required, get_jwt_identity

index = Blueprint('index', __name__)
logger = logging.getLogger('root')


@index.route('/create/file/<file_id>', methods=['POST'])
@jwt_required()
def add_index_for_file(file_id):
    user_id = get_jwt_identity()
    return add_index(user_id, file_id)


@index.route('/create/confuluence/<file_id>', methods=['POST'])
@jwt_required()
def add_index_for_confuluence(file_id):
    user_id = get_jwt_identity()
    return add_index(user_id, file_id)


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
