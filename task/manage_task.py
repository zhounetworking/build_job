#!/usr/bin/python
#-*- coding:utf8 -*-
#

import os
os.environ['CELERY_CONFIG_MODULE'] = 'task.celeryconfig'

from celery.task.control import inspect
from celery.result import AsyncResult as async


def get_active_task_list():
	active_task_list = []

	active = inspect()
	tasks_info = active.active()

	for task_instance in tasks_info:
		active_task_list.extend( tasks_info[task_instance] )

	return active_task_list


def get_task_result(task_id):
	task = async(task_id)
	return task.result


def revoke_task(task_id):
	task = async(task_id)
	if not task.ready():
		task.revoke(terminate=True)
		#task.revoke(terminate=True,signal='SIGKILL')


''' active task info
      {
         "args": "(1, 47)", 
         "time_start": 89826.308390651, 
         "name": "tasks.add", 
         "delivery_info": {
            "priority": 0, 
            "redelivered": null, 
            "routing_key": "celery", 
            "exchange": "celery"
         }, 
         "hostname": "celery@opstools", 
         "acknowledged": true, 
         "kwargs": "{}", 
         "id": "380b1a43-9db9-4e1c-a399-6c8ab6ddb3ef", 
         "worker_pid": 10442
      }
'''		
