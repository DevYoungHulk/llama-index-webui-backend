from flask import Blueprint
from pathlib import Path
import logging
from ..db import db
from ..services.index_mangement import add_index, remove_index

index = Blueprint('index', __name__)
logger = logging.getLogger('root')

@index.route('/<user_id>/create/<file_id>', methods=['POST'])
def add(user_id, file_id):
    return add_index(user_id, file_id)


@index.route('/<user_id>/remove/<file_id>', methods=['DELETE'])
def remove(user_id, file_id):
    return remove_index(user_id, file_id)
