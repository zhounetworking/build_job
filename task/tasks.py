#!/usr/bin/python
#-*- coding:utf8 -*-

import time
import json
import commands

from celery.task import task

from conf.config import *
from conf.game_config import game_info
from conf.redis_config import redis_client as rc

from lib.utils import log,notification
from lib.csv_get import csv_download
from lib.build_job import build_job,choose_jenkins,build_job_handle,check_job_status 

'''
   用root启动celery
'''
from celery import platforms
platforms.C_FORCE_ROOT = True


def num(assign_time):
    return int(assign_time) - int(time.time())

#def time_job_run(job_list_str,oss2_task_id,assign_time=None):

@task
def time_job_run(api_data):
    '''
        定时任务
        game_info = {
           'time'      : unixtime,
           'sign'      : sign,
           'project'   : project,
           'p_id'      : p_id,
           'p_name'    : p_name,
           'list_url'  : list_url,
           'u_type'    : u_type,
           'oss2_task_id'   : oss2_task_id,
           'success'   : -1,
           'msg'       : 'time_send_msg',  # 定时任务标识
         }
    '''
    celery_task_id = time_job_run.request.id

    data            = json.loads(api_data)
    assign_time     = data['time']
    timing          = data['timing']            # 是否定时, 1 定时 , 0 不定时
    p_id            = data['p_id']
    p_name          = data['p_name']
    csv_list        = data['list_url']          # 加 CSV 下载 , 上传到服务器
    u_type          = data['u_type']
    oss2_task_id    = data['oss2_task_id']

    job_list_str         = game_info[p_id][u_type]['context']

    if timing:
        print('%s %s, Wait for %d second , %d minutes' % (
        time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(assign_time))),
        job_list_str,
        num(assign_time),
        num(assign_time)/60
            )
        )

    while num(assign_time) > 0 :
        time.sleep(1)

        ''' 大于10分钟的, 直接sleep 10*60  '''
        if num(assign_time) > 10 * 60:
            time.sleep(10*60)
            print('%s %s, Wait for %d second , %d minutes' % (
                time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(assign_time))), 
                job_list_str, 
                num(assign_time), 
                num(assign_time)/60 
                )
            )
    else:
        return engine(oss2_task_id,celery_task_id,p_id,u_type,csv_list)



def engine(oss2_task_id,celery_task_id,p_id,u_type,csv_list):
    '''
        job_list_str    : 任务字符串 , 如 pp1_kk_hot_list  
        oss2_task_id    : OSS2 传过来的 id
        celery_task_id  : Celery 任务id
    '''
    start  = time.time()
    rc.hset(oss2_task_id,'task_id',celery_task_id)

    # csv download and upload to server
    err_csv_list = csv_down(csv_list,game_info[p_id]['local_csv_path'])
    if err_csv_list:
        return {
            "celery_err_msg": "csv download err", 
            "err_csv_list": err_csv_list, 
            "update_type": u_type, 
            "platform_id":p_id
        }

    if csv_upload(p_id) != 0:
        return { 
            "celery_err_msg": 'upload csv to server err,%s'%game_info[p_id]['front_server_ip'], 
            "update_type": u_type, 
            "platform_id":p_id
        }

    res   = []
    check = lambda x: x in ['FAILURE','None',None]
    jenkins_job_list = game_info[p_id][u_type]['command']
    jenkins_list_txt = game_info[p_id][u_type]['jenkins']
    jenkins_info     = choose_jenkins(jenkins_list_txt)

    for job in jenkins_job_list:
        job_name = job[0]
        rc.hset(oss2_task_id,'job_name',job_name)

        print('startting %s, sleep %s'%(job_name,job_exec_interval))
        time.sleep(job_exec_interval)

        stat = build_job_handle(jenkins_info,job)
        notification(stat)

        res.append(stat)
        if check(stat['stat']): break
        # 任务失败后,重复执行一次
        #if check(stat['stat']):
        #    stat = build_job_handle(job)
        #    notification(stat)
        #    res.append(stat)

        #    if check(stat['stat']): break
        #else:
        #    res.append(stat) 

    rc.hset(oss2_task_id,'job_name','ALL_JOB_DONE')
    end  = time.time()
    check_job_status(res,p_id,u_type) 

    return {
        'start_time': start,
        'end_time'  : end,
        'result'    : res,
        'args'      : game_info[p_id]['name'],
        'task_id'   : celery_task_id,
    }


def csv_down(csv_list,csv_path):
    '''
        download csv ok  : return empty list
        download csv fail: return err file list

    '''
    csv = csv_download(csv_list,csv_path)
    csv.run()
    return csv.download_err

def csv_upload(p_id):
    '''
        upload csv file to frontserver
    '''
    local_csv_path = game_info[p_id]['local_csv_path']
    front_csv_path = game_info[p_id]['front_csv_path']
    front_server_ip= game_info[p_id]['front_server_ip']

    rsync_cmd = 'rsync -vza --progress --delete %s root@%s:%s'%(
        local_csv_path,
        front_server_ip,
        front_csv_path
    )

    cmd_result = commands.getstatusoutput(rsync_cmd)
    log.info(rsync_cmd)
    log.info('rsync result: %s  %s'%( cmd_result[0],'success' if cmd_result[0] == 0 else 'fail'))
    log.info(cmd_result[1])
    return cmd_result[0]


