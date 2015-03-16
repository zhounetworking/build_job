#!/usr/bin/python
#-*- coding:utf8 -*-
#

import redisco
from redisco.containers import SortedSet

redis_host = '127.0.0.1'
redis_port = 6379
redis_db   = 0
redisco.connection_setup(
    host = redis_host,
    port = redis_port,
    db   = redis_db
)

redis_client = redisco.get_client()

redis_pubsub_channel = 'jenkins_task'

# Been to perform tasks id
redis_sortedset_key  = 'celery_task_id_sort_set'
task_id_sortset 	 = SortedSet(redis_sortedset_key)
