from flask_login import login_user, logout_user
from flask import Blueprint, request
import logging
from ..models.types import User
from flask_jwt_extended import jwt_required, create_access_token

user = Blueprint('user', __name__)
logger = logging.getLogger('root')


@user.route('/register', methods=['POST'])
def register():
    # 获取注册请求中的用户名和密码信息
    username = request.json.get('username')
    password = request.json.get('password')

    # 检查用户名是否已经存在
    existing_user = User.objects(username=username)
    if existing_user:
        return {'msg': 'Username already exists'}, 400
    user = User(username=username)
    user.update_password(password)
    # 在数据库中创建新用户
    user.save()

    return {'msg': 'Registration successful'}, 200


@user.route('/login', methods=['GET', 'POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.objects(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        access_token = create_access_token(identity=user.id)
        return {'message': 'Login successful', 'token': access_token}, 200
    return {'message': 'Invalid username or password'}, 401


@user.route('/logout')
@jwt_required
def logout():
    logout_user()
    return {'message': 'Logout successful'}, 200
