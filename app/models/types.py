import uuid
import os
from datetime import datetime
import pytz
import json
from bson.json_util import dumps
from mongoengine import *
from llama_index.core.types import MessageRole


def dict2obj(dic, objclass):

    # using json.loads method and passing json.dumps
    # method and custom object hook as arguments
    return json.loads(dumps(dic), object_hook=objclass)


class File(Document):
    id = UUIDField(primary_key=True, binary=True)
    file_name = StringField(max_length=100, required=True)
    root_path = StringField(max_length=100, required=True)
    file_path = StringField(max_length=100, required=True)
    file_full_path = StringField(max_length=100, required=True)
    temp_path = StringField(max_length=100, required=True)
    temp_full_path = StringField(max_length=100, required=True)
    md5 = StringField(max_length=100, required=True)
    user_id = StringField(max_length=100, required=True)
    indexed = BooleanField(required=False)

    def __init__(self, file_name, root_path, user_id, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.file_name = file_name
        self.root_path = root_path

        self.temp_path = os.path.join(root_path, 'cache', user_id)
        self.temp_full_path = os.path.join(self.temp_path, self.id)

        self.file_path = os.path.join(root_path, user_id)
        self.file_full_path = os.path.join(self.file_path, self.id)

    def to_dict(self):
        return json.loads(self.to_json())


class ChatHistory(Document):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    user_id = StringField(max_length=100, required=True)
    role = EnumField(MessageRole, required=True)
    content = StringField(required=True)
    date = StringField(required=True)

    def __init__(self, user_id, role, content, date, *args, **values):
        super().__init__(*args, **values)
        self.user_id = user_id
        self.role = role
        self.content = content
        self.date = date

    def to_dict(self):
        return json.loads(self.to_json())
