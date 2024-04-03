from app import create_app
import traceback
from flask import jsonify
from flask_cors import CORS
import os
import logging
# 默认为开发环境，按需求修改
config_name = os.environ.get('ENV_NAME', 'development')

app = create_app(config_name)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

logger = logging.getLogger('root')


@app.errorhandler(Exception)
def handle_exception(e):
    traceback_text = traceback.format_exc()
    error_message = {'msg': str(e)}
    logger.error(error_message)
    logger.error(traceback_text)
    response = jsonify(error_message)
    response.status_code = 500 if isinstance(e, Exception) else 400
    return response


if __name__ == '__main__':
    if config_name == 'development':
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)
