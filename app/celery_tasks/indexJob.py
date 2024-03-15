import mongoengine
from app.celery_tasks import celery_app
from app.services.index_mangement import *
import logging
import celery
import time
import traceback
from app.config import config
import mongoengine
logger = logging.getLogger('root')



@celery_app.task
def task(name, age):
    print("准备执行任务啦")
    time.sleep(3)
    return f"name is {name}, age is {age}"


@celery_app.task
def create_index_task(user_id, file_id):
    current_config = config['development']
    # logger.info('------- celery init '+__name__+'-------')
    # # # logger.info(__name__)
    # # logger.info(current_config.MONGO_DB_NAME)
    # # logger.info(current_config.MONGO_URI)
    # mongoengine.DEFAULT_CONNECTION_NAME = current_config.MONGO_URI
    # mongoengine.DEFAULT_DATABASE_NAME = current_config.MONGO_DB_NAME
    mongoengine.connect(current_config.MONGO_DB_NAME, host=current_config.MONGO_URI)
    try:
        result = add_index(user_id, file_id)
        return result
    except Exception as e:
        unlockFile(user_id, file_id)
        traceback_text = traceback.format_exc()
        logger.info(traceback_text)
        logger.error('create_index_task error')
        logger.error(e)
        return 'failed'
