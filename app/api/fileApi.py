
from flask import Blueprint, request
import logging
from ..services.file_management import delete, list_all, add
from bson.json_util import dumps, loads

file = Blueprint('file', __name__)
logger = logging.getLogger('root')


@file.route('/<user_id>/list', methods=['GET'])
def list_file(user_id):
    return list_all(user_id)


@file.route('/<user_id>/<file_id>', methods=['DELETE'])
def delete_file(user_id, file_id):
    return delete(user_id, file_id)


@file.route('/<user_id>/add', methods=['POST'])
def add_file(user_id):
    file = request.files['file']
    return add(file, user_id)
