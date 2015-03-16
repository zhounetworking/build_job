#!/usr/bin/python
#-*- coding:utf8 -*-
#
# 只作为 资源热更新 用
# 3. 需要把任务更新相关的机器的任务执行数 增大 
#
# 4. 实例化 Jenkins 类时，需要检查 用户名密码是否输的对i (HTTPError) , 是否连的上 jenkins  ( ConnectionError )
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


from conf.config import *
from lib.utils  import Mail,log,notification

from task.manage_task import revoke_task,get_active_task_list

import socket
socket.setdefaulttimeout(connect_jenkins_timeout)



def build_job(job_name, jenkins_url,username="",passwd=""):
	status             = {}
	status['error']    = []
	status['stat'] 	   = None
	status['last_no']  = None
	status['next_no']  = None
	status['params']   = None
	status['run_time'] = None
	status['job_name'] = job_name[0]

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
		#print 'job in queued ...'
		time.sleep(1)
	else:
		
		if job.get_last_buildnumber() > s_last:
			e_last = job.get_last_build()
		else:
			status['error'].append("job_number_err")
			return status

	while e_last.is_running():
		#print job.get_last_buildnumber()," running ..."
		time.sleep(2)
	else:
		if e_last.is_good() and e_last.get_status() == 'SUCCESS':
			status['stat'] = 'SUCCESS'
		else:
			status['stat'] = 'FAILURE'
			status['error'].append("job_appfail_err")

		status['last_no'] = s_last
		status['next_no'] = e_last.buildno


	status['run_time'] = e_last.get_duration().total_seconds()
	return status
	
	#last_build.get_console()

def main(p_job_list,jenkins_url):
    res = []

    for job in p_job_list:
        print('startting %s, sleep %s'%(job[0],job_exec_interval))
        time.sleep(job_exec_interval)

        #if '启动cmmsvrd' in job[0]:
        #    print "%s  sleep " % job[0]
        #    time.sleep( start_cmm_interval * 60 * 60 )

        print('%s is start'%job[0])
        stat = build_job(job,jenkins_url,jenkins_user,jenkins_passwd)

        notification(stat)
        res.append(stat)
        #log.info(res)

        if stat['stat'] == 'FAILURE':
            break

    return res


def check_job_status(res_list):
	mail_to.extend(mail_to_qa)

	mail = partial( Mail,
		user   = papasg_user,
		passwd = papasg_passwd,
		mail_to= mail_to,
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

	#log.info(mail_text)
	mail(mail_text=mail_text)

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
