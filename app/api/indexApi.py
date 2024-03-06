from flask import Blueprint
import logging
from ..services.index_mangement import add_index, remove_index
from flask_jwt_extended import jwt_required, get_jwt_identity

index = Blueprint('index', __name__)
logger = logging.getLogger('root')


@index.route('/create/<file_id>', methods=['POST'])
@jwt_required()
def add(file_id):
    user_id = get_jwt_identity()
    return add_index(user_id, file_id)


@index.route('/remove/<file_id>', methods=['DELETE'])
@jwt_required()
def remove(file_id):
    user_id = get_jwt_identity()
    return remove_index(user_id, file_id)
