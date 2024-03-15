from app.config import config
from celery import Celery
import mongoengine
import logging
logger = logging.getLogger('root')

current_config = config['development']
logger.info('------- celery init '+__name__+'-------')
# # logger.info(__name__)
# logger.info(current_config.MONGO_DB_NAME)
# logger.info(current_config.MONGO_URI)
mongoengine.DEFAULT_CONNECTION_NAME = current_config.MONGO_URI
mongoengine.DEFAULT_DATABASE_NAME = current_config.MONGO_DB_NAME

celery_app = Celery(__name__, broker=current_config.CELERY_BROKER_URL,
                    backend=current_config.CELERY_RESULT_BACKEND)
# celery_app.config_from_object('celery_tasks.celeryconfig')
