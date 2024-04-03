from llama_index.core.types import ChatMessage
import uuid
import os
from datetime import datetime
import pytz
import json
from bson.json_util import dumps
from mongoengine import *
from llama_index.core.types import MessageRole
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from flask_login import UserMixin
from enum import Enum
from typing import Union
from flask import Response


def dict2obj(dic, objclass):

    # using json.loads method and passing json.dumps
    # method and custom object hook as arguments
    return json.loads(dumps(dic), object_hook=objclass)


class User(UserMixin, Document):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    meta = {'collection': 'users'}

    def get_id(self):
        return self.username

    def update_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class BaseFile(Document):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    group_id = StringField(max_length=100, required=True)
    # normal_file = EmbeddedDocumentField(NormalFile, required=False)
    # confuluence = EmbeddedDocumentField(Confuluence, required=False)
    indexed = BooleanField(required=False)
    indexing = BooleanField(required=False)
    node_ids = ListField(required=False)
    ref_doc_ids = ListField(required=False)

    meta = {'collection': 'files',
            'allow_inheritance': True}

    def to_dict(self):
        return json.loads(self.to_json())


class Confuluence(BaseFile):
    group_key = StringField(max_length=100, required=False)
    space = StringField(max_length=100, required=False)
    page_id = StringField(max_length=100, required=False)
    include_children = BooleanField(required=False, default=False)
    include_attachments = BooleanField(required=False, default=False)


class NormalFile(BaseFile):
    # type = 'file'
    file_name = StringField(max_length=100, required=True)
    root_path = StringField(max_length=100, required=True)
    md5 = StringField(max_length=100, required=True)
    temp_path = StringField(max_length=100, required=True)
    temp_full_path = StringField(max_length=100, required=True)
    file_path = StringField(max_length=100, required=True)
    file_full_path = StringField(max_length=100, required=True)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if not self.temp_path:
            self.fix_full_info()

    def fix_full_info(self):
        self.temp_path = os.path.join(self.root_path, 'cache', self.group_id)
        self.temp_full_path = os.path.join(self.temp_path, str(self.id))
        self.file_path = os.path.join(self.root_path, self.group_id)
        self.file_full_path = os.path.join(self.file_path, str(self.id))


class MysqlConnector(BaseFile):
    host = StringField(max_length=100, required=True)
    port = StringField(max_length=100, required=True)
    user = StringField(max_length=100, required=True)
    password = StringField(max_length=100, required=True)
    database = StringField(max_length=100, required=True)
    table = StringField(max_length=100, required=True)


class FileType(Enum):
    ALL = 'all'
    FILE = 'normal'
    CONFLUENCE = 'confluence'
    MYSQL = 'mysql'
    MONGO = 'mongo'


class BaseLoaderConfig(Document):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    group_id = StringField(max_length=100, required=True)
    meta = {'collection': 'llm_configs',
            'allow_inheritance': True}

    def to_dict(self):
        return json.loads(self.to_json())


class ConfuluenceLoaderConfig(BaseLoaderConfig):
    base_url = StringField(max_length=100, required=True)
    api_token = StringField(max_length=100, required=False)

    # access_token = StringField(max_length=100, required=False)
    # token_type = StringField(max_length=100, required=False)
    # client_id = StringField(max_length=100, required=False)


class ChatGroup(Document):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    user_id = StringField(max_length=100, required=True)
    group_name = StringField(max_length=100, required=True)
    meta = {'collection': 'chat_group'}

    def to_dict(self):
        return json.loads(self.to_json())


class ChatHistory(Document):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    group_id = StringField(max_length=100, required=True)
    role = EnumField(MessageRole, required=True)
    content = StringField(required=True)
    date = StringField(required=True)
    meta = {'collection': 'chat_history'}

    def to_dict(self):
        return json.loads(self.to_json())

    def toChatMessage(self):
        return ChatMessage(
            role=self.role,
            content=self.content,
        )


class ModelType(Enum):
    OPENAI = 'openai'
    HUGGINGFACE = 'huggingface'
    OLLAMA = 'ollama'


class ChatModelConfig(EmbeddedDocument):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    model_type = EnumField(ModelType, required=True)
    model_name = StringField(max_length=100, required=True)
    openai_api_key = StringField(max_length=100, required=False)
    # meta = {'collection': 'chat_model_config'}

    # def to_dict(self):
    #     return json.loads(self.to_json())


# class EmbeddedModelConfig(EmbeddedDocument):
#     id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
#     model_name = StringField(max_length=100, required=True)
#     # meta = {'collection': 'embedded_model_config'}

#     # def to_dict(self):
#     #     return json.loads(self.to_json())

# # Index Config Types Enum


class IndexType(Enum):
    VECTOR = 'vector'
    KNOWLEDGE_GRAPH = 'knowlege_graph'
    SUMMARY = 'summary'
    KEYWORD = 'keyword'

# Index Storage Config Types Enum


class IndexStorageType(Enum):
    LOCAL = 'local'
    MONGO = 'mongo'
    NEO4j = 'neo4j'


class IndexConfig(EmbeddedDocument):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    config_type = EnumField(IndexType, required=True)
    description = StringField(max_length=200, required=False)
    similarity_top_k = IntField(required=False, default=3)
    storage_type = EnumField(IndexStorageType, required=True)
    uri = StringField(max_length=200, required=False)
    database = StringField(max_length=100, required=False)
    # namespace = StringField(max_length=15, required=True)
    username = StringField(max_length=100, required=False)
    password = StringField(max_length=100, required=False)


class RetrieverMode(Enum):
    OR = 'or'
    AND = 'and'


class RetriverConfig(EmbeddedDocument):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    indexs = ListField(required=False)
    mode = EnumField(RetrieverMode, required=False)


class ChatConfig(Document):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    group_id = StringField(max_length=100, required=True)
    chat_model = EmbeddedDocumentField(ChatModelConfig, required=False)
    embedded_model = EmbeddedDocumentField(ChatModelConfig, required=False)
    index_store_configs = EmbeddedDocumentField(IndexConfig, required=False)
    store_configs = ListField(
        EmbeddedDocumentField(IndexConfig), required=False)
    retriever = EmbeddedDocumentField(RetriverConfig, required=False)
    system_prompt = StringField(max_length=1024, required=False)

    def to_dict(self):
        return json.loads(self.to_json())