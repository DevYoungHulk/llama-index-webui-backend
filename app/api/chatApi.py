
from datetime import datetime
from llama_index.core.types import MessageRole
from ..models.types import *
from ..db import db
from flask import Blueprint, request
import logging
from bson.json_util import dumps, loads
from ..services.chat_context import get_gloabl_chat_agent_instance
chat = Blueprint('chat', __name__)
logger = logging.getLogger('root')


@chat.route('/<user_id>', methods=['POST'])
def chat_(user_id):
    question = request.json['question']
    date_q = datetime.now(
        pytz.timezone('Asia/Shanghai')).isoformat()
    chat_q = ChatHistory(
        user_id=user_id, role=MessageRole.USER, content=question, date=date_q)
    chat_q.save()
    try:
        answer = str(get_gloabl_chat_agent_instance().getAgent(
            user_id).chat(question))
    except Exception as e:
        return {'msg': str(e)}, 500
    date_a = datetime.now(
        pytz.timezone('Asia/Shanghai')).isoformat()
    chat_a = ChatHistory(
        user_id=user_id, role=MessageRole.ASSISTANT, content=answer, date=date_a)
    chat_a.save()
    return {'msg': 'success', 'data': answer}, 200


@chat.route('/history/<user_id>', methods=['GET'])
def get_history(user_id):
    res = ChatHistory.objects(user_id=user_id)
    result = []
    for i in res:
        result.append(i.to_dict())
    return {'msg': 'success', 'data': result}, 200


@chat.route('/clear/<user_id>', methods=['POST'])
def clear_history(user_id):
    res = ChatHistory.objects(user_id=user_id).delete()
    logger.info(res)
    agents = get_gloabl_chat_agent_instance().global_agents
    if user_id in agents:
        del agents[user_id]
    return {'msg': 'success'}
