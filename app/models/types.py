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


class File(Document):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    file_name = StringField(max_length=100, required=True)
    root_path = StringField(max_length=100, required=True)
    md5 = StringField(max_length=100, required=True)
    user_id = StringField(max_length=100, required=True)
    indexed = BooleanField(required=False)

    meta = {'collection': 'files'}

    def get_temp_path(self):
        return os.path.join(self.root_path, 'cache', self.user_id)

    def get_temp_full_path(self):
        return os.path.join(self.get_temp_path(), str(self.id))

    def get_file_path(self):
        return os.path.join(self.root_path, self.user_id)

    def get_file_full_path(self):
        return os.path.join(self.get_file_path(), str(self.id))

    def to_dict(self):
        return json.loads(self.to_json())


class ChatHistory(Document):
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    user_id = StringField(max_length=100, required=True)
    role = EnumField(MessageRole, required=True)
    content = StringField(required=True)
    date = StringField(required=True)
    meta = {'collection': 'chat_history'}

    def to_dict(self):
        return json.loads(self.to_json())
