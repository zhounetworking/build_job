#!/usr/bin/python
#-*- coding:utf8 -*-
#
#


import sys
from lib.build_job import *


if __name__ == '__main__':
	# 新平台加入,  在 lib/config.py 加入新平台的流程, 并在 job_dict 加入key即可
	job_dict = {
        "test_hot_job_list": test_hot_job_list ,
        "andriod_test_job_list": andriod_test_job_list ,

        # Thailand
        "th_hot_job_list"  : th_hot_job_list   ,
        "th_stop_job_list" : th_stop_job_list   ,
        "th_start_cmm"     : th_start_cmm ,

        # Taiwan
        "hmt_hot_job_list" : hmt_hot_job_list  ,
        "hmt_stop_job_list": hmt_stop_job_list  ,
        "hmt_start_cmm"    : hmt_start_cmm ,

        # Kaokao
        "kk_hot_job_list"  : kk_hot_job_list   ,
        "kk_stop_job_list" : kk_stop_job_list   ,
        "kk_start_cmm"     : kk_start_cmm ,

        # Korea
        "kr_hot_job_list"  : kr_hot_job_list   ,
        "kr_stop_job_list" : kr_stop_job_list   ,
        "kr_start_cmm"     : kr_start_cmm ,

        # Japan
        "jp_hot_job_list"  : jp_hot_job_list   ,
        "jp_stop_job_list" : jp_stop_job_list   ,
        "jp_start_cmm"     : jp_start_cmm ,
        
        # IOS
        "ios_hot_job_list" : ios_hot_job_list  ,                                              
        "ios_stop_job_list": ios_stop_job_list ,                                              
        "ios_start_cmm"    : ios_start_cmm ,

        # APP
        "app_hot_job_list" : app_hot_job_list ,
        "app_stop_job_list": app_stop_job_list ,
        "app_start_cmm"    : app_start_cmm ,

        # Tencent
        "qq_hot_job_list"  : qq_hot_job_list   ,
        "qq_stop_job_list" : qq_stop_job_list  ,
        "qq_start_cmm"     : qq_start_cmm ,

        # Andriod
        "andriod_hot_job_list" : andriod_hot_job_list  ,
        "andriod_stop_job_list": andriod_stop_job_list ,
        "andriod_start_cmm"    : andriod_start_cmm ,
	}

	k = job_dict.keys()
	k.sort()

	try:
		job_list = sys.argv[1]
		if job_list not in job_dict:
			raise Exception
	except:
		print('Please enter the update type:')
		a = 0
		for job in k:
			print('\t%s'%job)
			a += 1
			if a%2 == 0:
				print '\n'
		exit(0)


	if UPDATE_DEBUG:
		res = main(job_dict[job_list], jenkins_url_test)	# 测试
	else:
		res = main(job_dict[job_list], jenkins_url)

	check_job_status(res)
