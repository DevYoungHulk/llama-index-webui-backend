import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# base configuration
class Config:
    SECRET_KEY = os.environ.get('KEY') or '123456'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # 数据库规则
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True


# 开发环境
class DevelopmentConfig(Config):
    MONGO_DB_NAME = 'llama-index-dev'
    MONGO_USERNAME = 'root'
    MONGO_PASSWORD = 'example'
    MONGO_HOST = '127.0.0.1:27017'
    MONGO_URI = 'mongodb://%s:%s@%s/%s?authSource=admin' % (
        MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST, MONGO_DB_NAME)

    SECRET_KEY = 'a8ef2798c4e84a0744da509c5da07e30'
    JWT_SECRET_KEY = 'ydYdTpdGaF5KnPcPa_UeARTgEIzzpXjemQ8rnZ9ZhFA'
    JWT_ACCESS_TOKEN_EXPIRES = 43200  # Expires in 12 hour
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days


# 测试环境
class TestingConfig(Config):
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
    MONGO_HOST = os.environ.get('MONGO_HOST')
    MONGO_URI = 'mongodb://%s:%s@%s/%s?authSource=admin' % (
        MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST, MONGO_DB_NAME)

    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Expires in 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days


# 生产环境
class ProductionConfig(Config):
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
    MONGO_HOST = os.environ.get('MONGO_HOST')
    MONGO_URI = 'mongodb://%s:%s@%s/%s?authSource=admin' % (
        MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST, MONGO_DB_NAME)

    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Expires in 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days


# config dict
# 生成一个字典，用来根据字符串找到对应的配置类
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
