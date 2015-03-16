#!/usr/bin/python
#-*- coding:utf8 -*-
#
#


import sys
from lib.build_job import *


# 新平台加入,  在 lib/config.py 加入新平台的流程, 并在 job_dict 加入key即可
job_dict = {
        'test1': test1 ,
        'test2': test2 ,
        'test3': test3 ,
        'test_api': test_api ,

        'test_hot_job_list': test_hot_job_list ,
        'andriod_test_job_list': andriod_test_job_list ,

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



class Run(object):
    def __init__(self,job_list):
        self.status = False
        self.job_list = job_list

    def callback(self):
        self.status = True

    def run(self):
        #jenkins_url_test = 'http://jenkins.hrgame.com:8080/'                                          

        if UPDATE_DEBUG:
            result = main(job_dict[self.job_list], jenkins_url_test)    # 测试
        else:
            result = main(job_dict[self.job_list], jenkins_url)

        # res: result list of jobs done
        check_job_status(result)

        self.callback()

        #print('run success %s'%self.status)   
        return result

if __name__ == '__main__':
    pass
