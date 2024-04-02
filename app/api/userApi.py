from flask_login import login_user, logout_user
from flask import Blueprint, request
import logging
from app.models.types import User
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity

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
        refresh_token = create_refresh_token(identity=user.id)
        return {'msg': 'Login successful', 'token': access_token, 'refresh_token': refresh_token}, 200
    return {'msg': 'Invalid username or password'}, 401


@user.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    # Refresh the access token using the refresh token
    current_user = get_jwt_identity()
    if current_user:
        access_token = create_access_token(identity=current_user)
        refresh_token = create_refresh_token(identity=current_user)
        return {'msg': 'Login successful', 'token': access_token, 'refresh_token': refresh_token}, 200
    return {'msg': 'Invalid token'}, 401


@user.route('/logout')
@jwt_required
def logout():
    logout_user()
    return {'msg': 'Logout successful'}, 200
