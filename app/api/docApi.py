
from flask import Blueprint, request
import logging
from app.services.file_management import delete, list_all, add
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.types import FileType
doc = Blueprint('doc', __name__)
logger = logging.getLogger('root')


@doc.route('/<group_id>/<filetype>', methods=['GET'])
@jwt_required()
def list_file(filetype, group_id):
    return list_all(group_id, filetype)


@doc.route('/<group_id>/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id, group_id):
    return delete(group_id, file_id)


@doc.route('/<group_id>/<filetype>', methods=['POST'])
@jwt_required()
def add_file(filetype, group_id):
    if filetype == FileType.FILE.value:
        file = request.files['file']
        return add(group_id, filetype, file)
    elif filetype == FileType.CONFLUENCE.value:
        return add(group_id, filetype, request.json)
    else:
        return {"msg": "filetype not support"}, 409
