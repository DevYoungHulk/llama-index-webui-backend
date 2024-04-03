import logging
import os
import hashlib
from app.models.types import *
logger = logging.getLogger('root')

ALLOWED_EXTENSIONS = set(['pdf', 'txt', 'md'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def list_all( group_id, type):
    result = []
    if type == FileType.FILE.value or type == FileType.ALL.value:
        list_cur = NormalFile.objects(group_id=group_id)
        for i in list_cur:
            result.append(i.to_dict())
    if type == FileType.CONFLUENCE.value or type == FileType.ALL.value:
        list_cur = Confuluence.objects(group_id=group_id)
        for i in list_cur:
            result.append(i.to_dict())
    return {'data': result}


def delete(group_id, file_id):
    file: None | BaseFile = BaseFile.objects(
        id=file_id,group_id=group_id).first()
    if file:
        if 'indexed' in file and file['indexed']:
            return {'msg': 'delete failed, file indexed, please remove index first!'}
        os.remove(file.file_full_path)
        file.delete()
        return {'msg': 'delete success'}
    else:
        return {'msg': 'delete failed, file not esist!'}, 404


def add( group_id, type, file):
    if type == FileType.FILE.value:
        if file and allowed_file(file.filename):
            file_name = file.filename
            f = NormalFile(group_id=group_id, root_path='./temp',
                           file_name=file_name)
            if not os.path.exists(f.temp_path):
                os.makedirs(f.temp_path)
            file.save(f.temp_full_path)
            with open(f.temp_full_path, 'rb') as file_to_check:
                md5 = hashlib.md5(file_to_check.read()).hexdigest()
                f.md5 = md5

            if NormalFile.objects(group_id=group_id, md5=md5).first():
                os.remove(f.temp_full_path)
                return {'msg': 'file exsit'}
            elif NormalFile.objects(group_id=group_id, file_name=file_name).first():
                os.remove(f.temp_full_path)
                return {'msg': 'file name duplicate'}
            if not os.path.exists(f.file_path):
                os.makedirs(f.file_path)
            os.rename(f.temp_full_path, f.file_full_path)
            f.save()
            return {'msg': 'upload successed', 'data': f.to_dict()}
    elif type == FileType.CONFLUENCE.value:
        if Confuluence.objects(group_key=file['group_key']).first():
            return {'msg': 'Confuluence group_key duplicate'}
        else:
            confuluence = Confuluence(
                space=file['space'] if 'space' in file else None,
                page_id=file['page_id'] if 'page_id' in file else None,
                group_key=file['group_key'] if 'group_key' in file else None,
                include_children=file['include_children'] if 'include_children' in file else False,
                include_attachments=file['include_attachments'] if 'include_attachments' in file else False,
            )
            confuluence.save()

            return confuluence.to_dict()
    return {'msg': 'only alloy file type ' + str(ALLOWED_EXTENSIONS)}
