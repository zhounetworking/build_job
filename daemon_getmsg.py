#!/usr/bin/python
#-*- coding:utf8 -*-
#


import os
import sys
import time
import atexit
import traceback as t

from lib.utils import *
from conf.redis_config import * 

from lib.Run import Run,job_dict

from redisco.containers import SortedSet

# redis 重连

os.environ['CELERY_CONFIG_MODULE'] = 'task.celeryconfig'
from task.tasks import job_run,Job_run 

class pubsub_daemon(object):
    def __init__(self):
        self.status = True
        self.pubsub = pubsub_daemon.init_pubsub()

    @classmethod
    def init_pubsub(self):
        pubsub = redis_client.pubsub()  
        pubsub.subscribe(redis_pubsub_channel)
        
        return pubsub

    def at_exit_monitor(self,txt):
        stat = Mail(
            papasg_user,
            papasg_passwd,
            mail_to,
            smtp_server,
            'daemonDown', 
            txt
        )
        return stat

    def daemon(self, db):
        while True:
            message = self.pubsub.get_message()
            if message == None or message['data'] == 1:
                time.sleep(0.1)
                continue

            data    = message['data']

            log.info("message: %s *****************" % message)

#            if data in job_dict:
#                job = job_run.delay(data)
#                db.add(job.task_id, 1)
#                log.info("%s add task queue ... done" % data)
#            else:
#                log.info("[%s] not in task, don't add"% data)

            data = data.split(',')

            if data[0] in job_dict:
                if len(data) >= 2:
                    job = Job_run.delay(*data)
                elif len(data) == 1:
                    data= data[0]
                    job = job_run.delay(data)

                db.add(job.task_id, 1)
                log.info("%s add task queue ... done" % data)
            else:
                log.info("*%s* not in task, don't add"% data)


if __name__ == '__main__':
    daemon = pubsub_daemon()

    try:
        daemon.daemon( task_id_sortset )
    except:
        log.exception('daemon_Exit_Error')
        atexit.register(daemon.at_exit_monitor,t.format_exc())
