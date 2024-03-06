import logging
import os
from ..db import db
import hashlib
from ..models.types import File
logger = logging.getLogger('root')

ALLOWED_EXTENSIONS = set(['pdf', 'txt', 'md'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def list_all(user_id):
    list_cur = File.objects(user_id=user_id)
    result = []
    for i in list_cur:
        result.append(i.to_dict())
    return {'data': result}


def delete(user_id, file_id):
    file = File.objects(user_id=user_id, id=file_id).first()
    if file:
        if 'indexed' in file and file['indexed']:
            return {'msg': 'delete failed, file indexed, please remove index first!'}
        os.remove(file.get_file_full_path())
        file.delete()
        return {'msg': 'delete success'}
    else:
        return {'msg': 'delete failed, file not esist!'}


def add(file, user_id):
    if file and allowed_file(file.filename):
        file_name = file.filename
        f = File(file_name=file_name, root_path='./temp', user_id=user_id)

        if not os.path.exists(f.get_temp_path()):
            os.makedirs(f.get_temp_path())
        file.save(f.get_temp_full_path())
        with open(f.get_temp_full_path(), 'rb') as file_to_check:
            md5 = hashlib.md5(file_to_check.read()).hexdigest()
            f.md5 = md5

        if File.objects(user_id=user_id, md5=md5).first():
            os.remove(f.get_temp_full_path())
            return {'msg': 'file exsit'}
        elif File.objects(user_id=user_id, file_name=file_name).first():
            os.remove(f.get_temp_full_path())
            return {'msg': 'file name duplicate'}
        if not os.path.exists(f.get_file_path()):
            os.makedirs(f.get_file_path())
        os.rename(f.get_temp_full_path(), f.get_file_full_path())
        f.save()
        return {'msg': 'upload successed', 'data': f.to_dict()}
    return {'msg': 'only alloy file type ' + str(ALLOWED_EXTENSIONS)}
