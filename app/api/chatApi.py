
from llama_index.core.agent import ReActAgent
from datetime import datetime
from llama_index.core.types import MessageRole
from app.models.types import *
from flask import Blueprint, request
import logging
from app.services.chat_context import get_gloabl_chat_agent_instance, create_agent
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
chat = Blueprint('chat', __name__)
logger = logging.getLogger('root')


@chat.route('/<group_id>', methods=['POST'])
@jwt_required()
def chat_(group_id):
    question = request.json['question']
    date_q = datetime.now(
        pytz.timezone('Asia/Shanghai')).isoformat()
    logger.info('==========new question===========')
    logger.info(question)
    chat_q = ChatHistory(
        group_id=group_id, role=MessageRole.USER, content=question, date=date_q)
    chat_q.save()
    try:
        chat_config = ChatConfig.objects(group_id=group_id).first()
        agent: ReActAgent = create_agent(chat_config)
        response = agent.query(question)
        if hasattr(response, 'response_gen'):
            logger.info('-------response.response_gen----------')
            logger.info(response.response_gen)
        if hasattr(response, 'response_txt'):
            logger.info('-------response.response_txt----------')
            logger.info(response.response_txt)
        source_nodes = []
        if hasattr(response, 'source_nodes'):
            logger.info('-------response.source_nodes----------')
            logger.info(response.source_nodes)
            for node in response.source_nodes:
                source_nodes.append(
                    {'id': node.id_, 'text': node.text, 'score': node.score})
        answer = str(response)
        # answer = str(get_gloabl_chat_agent_instance().loadQueryEngineTool(user_id)[0].query_engine.query(question))
    except Exception as e:
        logger.error(traceback.format_exc())
        return {'msg': str(e)}, 500
    date_a = datetime.now(
        pytz.timezone('Asia/Shanghai')).isoformat()
    # answer = 'test answer ' + date_a

    chat_a = ChatHistory(
        group_id=group_id, role=MessageRole.ASSISTANT, content=answer, date=date_a)
    chat_a.save()
    return {'msg': 'success', 'data': {'answer': answer, 'source_nodes': source_nodes}}, 200


@chat.route('/<group_id>', methods=['GET'])
@jwt_required()
def get_history(group_id):
    res = ChatHistory.objects(group_id=group_id,)
    result = []
    for i in res:
        result.append(i.to_dict())
    return {'msg': 'success', 'data': result}, 200


@chat.route('/<group_id>/clear', methods=['POST'])
@jwt_required()
def clear_history(group_id):
    res = ChatHistory.objects(group_id=group_id).delete()
    logger.info(res)
    return {'msg': 'success'}


@chat.route('/<group_id>/<msg_id>', methods=['DELETE'])
@jwt_required()
def del_chat_msg(group_id, msg_id):
    res = ChatHistory.objects(
        group_id=group_id,  id=msg_id).delete()
    logger.info(res)
    return {'msg': 'success'}
