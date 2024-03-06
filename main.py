from app import create_app
import traceback
from flask import jsonify
import logging
# 默认为开发环境，按需求修改
config_name = 'development'

app = create_app(config_name)

logger = logging.getLogger('root')

@app.errorhandler(Exception)
def handle_exception(e):
    traceback_text = traceback.format_exc()
    error_message = {'msg': str(e), 'traceback': traceback_text}
    logger.error(error_message)
    response = jsonify(error_message)
    response.status_code = 500 if isinstance(e, Exception) else 400
    return response


if __name__ == '__main__':
    app.run()
