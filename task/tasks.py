#!/usr/bin/python
#-*- coding:utf8 -*-

import time

from lib.Run import Run
from celery.task import task


@task
def add(x, y):
    time.sleep(20000)
    return {'result':x + y , 'a':'a' }


@task
def wait_time(s):
    fix = int(s)
    while True:
        now = int(time.time())
        if now > fix:
            print 'task done'
            return now
        else:
            time.sleep(1)
            print 'fix: %s   now:%s    sleep' %(fix,now)



@task
def Job_run(job_type,assign_time=None):
    '''
        Assign time exec task
    '''
    num = int(assign_time) - int(time.time())
    print('%s %s, Wait for %d second , %d minutes' % (time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(assign_time))), job_type, num, num/60 ))

    while int(assign_time) - int(time.time()):
        time.sleep(1)
        num = int(assign_time) - int(time.time())
        if num > 10 * 60:
            time.sleep(10*60)
            num = int(assign_time) - int(time.time())
            print('%s %s, Wait for %d second , %d minutes' % (time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(assign_time))), job_type, num, num/60 ))
    else:
        result = {}
        start  = time.time()
        engine = Run(job_type)
        res = engine.run()
        end  = time.time()
        result['start_time'] = start  
        result['end_time']   = end
        result['result']     = res
        result['args']       = job_type
    return result


@task
def job_run(job_type):
    result = {}
    start  = time.time()
    engine = Run(job_type)
    res = engine.run()
    end  = time.time()
    result['start_time'] = start
    result['end_time']   = end
    result['result']     = res
    result['args']         = job_type
    return result 
