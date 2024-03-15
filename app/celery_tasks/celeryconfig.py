from datetime import timedelta

# BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
CELERY_ACCEPT_CONTENT = ['json']
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERYD_MAX_TASKS_PER_CHILD = 500
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = False
CELERY_IMPORTS = (
    'app.celery_tasks',
)
# CELERYBEAT_SCHEDULE = {
#     'test_reminders': {
#         'task': 'your_module_name.test',
#         'schedule': timedelta(seconds=60),
#         'args': None
#     },
# }