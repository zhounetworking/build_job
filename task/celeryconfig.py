#!/usr/bin/python
#-*- coding:utf8 -*-
#
# http://celery.readthedocs.org/en/latest/configuration.html
#

import sys
import os

#sys.path.append('../')
sys.path.append(
	os.path.dirname( os.getcwd() )
)

sys.path.insert(0, os.getcwd())

CELERY_IMPORTS = ('task.tasks', )


#'''
#    用root启动celery
#'''
#from celery import platforms
#platforms.C_FORCE_ROOT = True


from conf.redis_config import redis_host,redis_port,redis_db,redis_password

CELERY_REDIS_DB         = redis_db 
CELERY_REDIS_HOST       = redis_host
CELERY_REDIS_PASSWORD   = redis_password
CELERY_REDIS_PORT       = redis_port
#CELERY_RESULT_BACKEND = 'amqp'

# 'redis://:Hrgame@172.16.1.102:6379/0'
REDIS_CONFIG_INFO = 'redis://:%s@%s:%s/%s'%(
    CELERY_REDIS_PASSWORD,
    CELERY_REDIS_HOST,
    CELERY_REDIS_PORT,
    CELERY_REDIS_DB
) 

BROKER_URL = REDIS_CONFIG_INFO

# 任务运行超过 3600s, celery会将任务交给另外一个worker重新运行
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}

CELERY_RESULT_BACKEND = REDIS_CONFIG_INFO
CELERY_TASK_RESULT_EXPIRES = None

CELERY_SEND_TASK_SENT_EVENT= True
