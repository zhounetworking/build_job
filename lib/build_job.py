#!/usr/bin/python
#-*- coding:utf8 -*-
#

import os
import sys 
import time
import json 
import traceback
import jenkinsapi
from functools import partial
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.custom_exceptions import WillNotBuild


from conf.config import * # job_dict,jenkins_dic
from conf.game_config import game_info

from lib.utils  import Mail,log,notification

from task.manage_task import revoke_task,get_active_task_list

import socket
socket.setdefaulttimeout(connect_jenkins_timeout)



#def build_job(job_name, jenkins_url="",username="",passwd="",params={}):
def build_job(job_name, jenkins_url="",username="",passwd=""):
    status = {
        'error'     : [],
        'stat'      : None,
        'last_no'   : None,
        'next_no'   : None,
        'params'    : None,
        'run_time'  : None,
        'job_name'  : job_name[0],
    }

    if not isinstance(job_name, tuple):
        status['error'].append("job_name_not_tuple")
        return status

    try:
        j = Jenkins( jenkins_url,username,passwd )
    except:
        status['error'].append("connect_jenkins_err")
        return status

    if job_name[0] not in j.get_jobs_list():
        status['error'].append("job_not_exist")
        return status

# 为 jenkins任务 加参数
#    if params:
#        job = j.get_job(job_name[0],params)
#    else:
#        job = j.get_job(job_name[0])
    job = j.get_job(job_name[0])

    # when job running in first , get_last_buildnumber error
    try:
        s_last = job.get_last_buildnumber()
    except:
        s_last = 0

    # if job running now, stop it!
    if job.is_queued():
        status['error'].append("before_is_queued")
        return status
    elif job.is_running():
        s_last_job = job.get_last_build()
        if s_last_job.stop():
            status['stop_before_running'] = True
        else:
            status['stop_before_running'] = False
            return status
            
    try:
        if len(job_name) > 1:
            j.build_job( job_name[0], job_name[1] )
            status['params'] = job_name[1]
        else:
            j.build_job( job_name[0])
    except WillNotBuild:
        status['error'].append("job_run_err")
        return status
        #return traceback.print_exc()
    except Exception:
        log.exception('otherError')
        status['error'].append("other_error")
        return status

    # In the quiet period of jenkins
    while job.is_queued():
        time.sleep(1)
    else:
        
        if job.get_last_buildnumber() > s_last:
            e_last = job.get_last_build()
        else:
            status['error'].append("job_number_err")
            return status

    while e_last.is_running():
        time.sleep(1)
    else:
        if e_last.is_good() and e_last.get_status() == 'SUCCESS':
            status['stat'] = 'SUCCESS'
        else:
            status['stat'] = 'FAILURE'
            status['error'].append("job_appfail_err")

        status['last_no'] = s_last
        status['next_no'] = e_last.buildno

    status['task_info']= e_last.get_console()
    status['run_time'] = e_last.get_duration().total_seconds()
    return status


def choose_jenkins(jenkins_job_list_txt):
    '''
    jenkins_job_list : 
        conf/config.py 中定义的任务名中的元组, 如 ('testjob',)
    jenkins_dic :
        jenkins 配置
    '''
    #job = jenkins_job_list[0]
    job = jenkins_job_list_txt

    if job.startswith('zgh') or job.startswith('zhanguo'):
        jenkins_info = jenkins_dic['zgh']
    elif job.startswith('lme'):
        jenkins_info = jenkins_dic['lme']
    elif job.startswith('pp2'):
        jenkins_info = jenkins_dic['pp2']
    elif job.startswith('pp1') or job.startswith('test'):
        jenkins_info = jenkins_dic['pp1']
    else:
        raise Exception, "No jenkins config info"

    print "job_list: %s ,url: %s"%(job,jenkins_info['url'])
    return jenkins_info

#def build_job_handle(jenkins_info,jenkins_job,params={}):
def build_job_handle(jenkins_info,jenkins_job):
    jenkins_url    = jenkins_info['url']
    jenkins_user   = jenkins_info['user']
    jenkins_passwd = jenkins_info['passwd']

    build_job_handle = partial(
        build_job,
        jenkins_url=jenkins_url,
        username=jenkins_user,
        passwd=jenkins_passwd,
#        params=params,
    )

    return build_job_handle(jenkins_job)



def check_job_status(res_list,p_id,u_type):
    # add qa mail
    MAIL_TO = mail_to[:]
    MAIL_TO.extend(mail_to_qa)

    # add designer mail
    if game_info[p_id]['messages']['inform']:
        try:
            MAIL_TO.extend(game_info[p_id]['messages']['design_mail'])
            print('add designer mail: %s'%game_info[p_id]['messages']['design_mail'])
        except:
            print('get platform name fail [ %s ]'%game_info[p_id][u_type]['context'])

    mail = partial( Mail,
        user   = papasg_user,
        passwd = papasg_passwd,
        mail_to= MAIL_TO,
        smtp_server = smtp_server,
        subject = subject    
    )

    success = True
    for res in res_list:
        if res['stat'] != 'SUCCESS':
            success = False
            err_job_name = res['job_name']

    if success:
        mail_text = mail_end_notify_ok
    else:
        mail_text = mail_end_notify_fail % err_job_name

    mail(subject=game_info[p_id][u_type]['context'],mail_text=mail_text)


if __name__ == '__main__':

    jenkins_url_test = 'http://jenkins.hrgame.com:8080/'
    stat = build_job(('客户端_04_同步资源到正式环境_FL越狱！！',{'ok':'no','Bool':False}),jenkins_url_test)

    if stat['stat']:
        notification(stat)
    else:
        print 'fail'

    check_job_status([ stat ])
    print json.dumps(stat,indent=3)
    print stat['job_name']
