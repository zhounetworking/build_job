import sys
import os

#sys.path.append('../')
sys.path.append(
    os.path.dirname( os.getcwd() )
)

sys.path.insert(0, os.getcwd())

CELERY_IMPORTS = ('task.tasks', )

#CELERY_RESULT_BACKEND = 'amqp'
BROKER_URL = 'redis://localhost:6379/0'

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 360}

CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_SEND_TASK_SENT_EVENT= True
