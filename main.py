from app import creat_app
import os

# 默认为开发环境，按需求修改
config_name = 'development'

app = creat_app(config_name)

if __name__ == '__main__':
    app.run()


# from flask import Flask, Request, request

# app = Flask(__name__)


# @app.before_request
# def hook():
#     # request - flask.request
#     print('endpoint: %s, url: %s, path: %s' % (
#         request.endpoint,
#         request.url,
#         request.path))
#     # just do here everything what you need...
#     print('------ 0 a='+request.args['a'])
#     if request.args['a'] == '1':
#         print(' --------- a=1')
#         return 'cus system error',500


# class Middleware:

#     def __init__(self, app):
#         self.app = app

#     def __call__(self, environ, start_response):
#         # not Flask request - from werkzeug.wrappers import Request
#         request = Request(environ)
#         print('Middleware path: %s, url: %s' % (request.path, request.url))
#         # just do here everything what you need
#         return self.app(environ, start_response)


# app.wsgi_app = Middleware(app.wsgi_app)


# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"
