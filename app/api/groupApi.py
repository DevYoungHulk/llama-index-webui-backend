
from flask import Blueprint, request
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.types import *
from flask import jsonify

chat_group = Blueprint('chat_group', __name__)
logger = logging.getLogger('root')


@chat_group.route('/list', methods=['GET'])
@jwt_required()
def list_groups():
    user_id = get_jwt_identity()
    groups = ChatGroup.objects(user_id=user_id)
    data = []
    for g in groups:
        data.append(g.to_dict())
    return {'msg': 'ok', 'data': data}


@chat_group.route('/create', methods=['POST'])
@jwt_required()
def create_group():
    user_id = get_jwt_identity()
    group_name = request.json.get('group_name')
    group = ChatGroup.objects(user_id=user_id, group_name=group_name).first()
    if group:
        return {'msg': 'group already exists'}, 409
    group = ChatGroup(user_id=user_id, group_name=group_name)
    group.save()
    return {'msg': 'ok', 'data': group.to_dict()}


@chat_group.route('/<group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    user_id = get_jwt_identity()
    group = ChatGroup.objects(user_id=user_id, id=group_id).first()
    return {'msg': 'ok', 'data': group.to_dict()} if group else {'msg': 'group not found'}, 404


@chat_group.route('/<group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    user_id = get_jwt_identity()
    res = ChatGroup.objects(user_id=user_id, id=group_id).first().delete()
    logger.info(res)
    return {'msg': 'ok'}


@chat_group.route('/<group_id>/config', methods=['POST'])
def create_or_update_config(group_id):
    new_config: ChatConfig = ChatConfig.from_json(json.dumps(request.json))
    logger.info('new config ->' + new_config.to_json())
    current_config = ChatConfig.objects(group_id=group_id).first()
    if current_config:
        for attr in current_config:
            if attr in ['_id', 'id', 'group_id'] or None == getattr(new_config, attr) or len(getattr(new_config, attr)) == 0:
                continue
            logger.info(attr)
            current_config.update(**{'set__'+attr: getattr(new_config, attr)})
        return {'msg': 'success', 'data': {'id': current_config.id}}

    else:
        new_config.group_id = group_id
        new_config.save()
        return {'msg': 'success', 'data': {'id': new_config.id}}



@chat_group.route('/<group_id>/config', methods=['GET'])
def get_config(group_id):
    res = ChatConfig.objects(group_id=group_id).first()
    logger.info(res)
    return {'msg': 'success', 'data': res.to_dict()}


@chat_group.route('/<group_id>/config', methods=['DELETE'])
def delete_config(group_id):
    res = ChatConfig.objects(group_id=group_id).delete()
    logger.info(res)
    return {'msg': 'success'}
