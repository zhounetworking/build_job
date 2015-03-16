#!/usr/bin/python
#-*- coding:utf8 -*-
#
#

import os
import time

#"""""""""""""""""""
#    @ GLOBAL CONFIGURATION
#"""""""""""""""""""

basedir = os.path.dirname(
    os.path.abspath(
        os.path.dirname(__file__)
    )
)



#"""""""""""""""""""
#    @ NOTIFICATION SETTING
#"""""""""""""""""""

papasg_user   = ""
papasg_passwd = ""

smtp_server   = ""

mail_to       = [ 
]

mail_to_qa      = [
]

subject       = "%s Game Update Mail"%time.strftime("%m-%d %H:%M",time.localtime())

mail_text     = '''
JOB STATUS  : %s
JOB ID      : %s 
JOB NAME    : %s 
JOB RUNTIME : %s 
JOB ERROR   : %s 
JOB PARAMS  : %s 
'''

mail_end_notify_ok   = ''' \
版本发布成功，请测试线上内容，如果验证通过，请通知到相关人员。
'''

mail_end_notify_fail = ''' \
%s 执行失败!  版本发布失败，请不要作线上测试，通知运维及策划人员。
'''


#"""""""""""""""""""
#    @ GAME CONFIGURATION
#"""""""""""""""""""

# jenkins master url

jenkins_user        = 'admin'
jenkins_passwd      = ''

jenkins_url         = 'http://jenkins.hrgame.com:8080/'
jenkins_url_test    = 'http://jenkins.hrgame.com:8080/'

# interval is minutes
job_exec_interval   = 10 

# start cmm , hour
start_cmm_interval  = 2

# timeout of connect jenkins server
connect_jenkins_timeout = 30

#===============  测试链接  ==================

#UPDATE_DEBUG = True
UPDATE_DEBUG = False


test_api = [
    ('test_api' , ),
]

