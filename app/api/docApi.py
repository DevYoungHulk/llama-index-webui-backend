
from flask import Blueprint, request
import logging
from app.services.file_management import delete, list_all, add
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.types import FileType
doc = Blueprint('doc', __name__)
logger = logging.getLogger('root')


@doc.route('/<group_id>/<filetype>/list', methods=['GET'])
@jwt_required()
def list_file(filetype, group_id):
    current_user = get_jwt_identity()
    if current_user:
        return list_all(current_user, group_id, filetype)
    else:
        return {"msg": "user not found"}, 401


@doc.route('/<group_id>/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id, group_id):
    current_user = get_jwt_identity()
    if current_user:
        return delete(current_user, group_id, file_id)
    else:
        return {"msg": "user not found"}, 401


@doc.route('/<group_id>/<filetype>/add', methods=['POST'])
@jwt_required()
def add_file(filetype, group_id):
    current_user = get_jwt_identity()
    if current_user:
        if filetype == FileType.FILE.value:
            file = request.files['file']
            return add(current_user, group_id, filetype, file)
        elif filetype == FileType.CONFLUENCE.value:
            return add(current_user, group_id, filetype, request.json)
        else:
            return {"msg": "filetype not support"}, 409
    else:
        return {"msg": "user not found"}, 401
