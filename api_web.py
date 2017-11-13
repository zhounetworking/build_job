#!/usr/bin/python
#-*- coding:utf8 -*-
#

import json
import time
import hashlib
import traceback

import tornado.ioloop
import tornado.web

from urllib import unquote

from lib.publish import *
from lib.utils import log

from conf.game_config import game_info
from conf.redis_config import task_id_sortset
from conf.config import ENABLE_KEY_AUTH, API_KEY

from task.manage_task import get_active_task_list ,get_task_result,revoke_task


settings = {'debug' : True}

def ret_json(data):
    try:
        return json.dumps(data)
    except:
        return json.dumps(data,ensure_ascii=False)
        #return json.dumps(data,encoding='latin1').decode('utf8')


def check_sign(sign):
    def Sign(fn):
        if not sign:
            return False

        TIME = time.strftime('%Y%m%d%H',time.localtime())
        if ENABLE_KEY_AUTH:
            return hashlib.md5(TIME+API_KEY).hexdigest() == sign
        else:
            return True
    return Sign


class time_send_msg(tornado.web.RequestHandler):
    def get(self):
        #msg      = self.get_argument('msg'      ,0)
        unixtime = self.get_argument('time'     ,0)
        timing   = self.get_argument('timing'   ,0)
        sign     = self.get_argument('sign'     ,0)

        project  = self.get_argument('project'  ,0)
        p_id     = self.get_argument('region'   ,0)
        p_name   = self.get_argument('p_name'   ,0)
        list_url = self.get_argument('list_url' ,0)
        u_type   = self.get_argument('u_type'   ,0)
        oss2_task_id  = self.get_argument('task_id','default_oss2_task_id')

        p_id   = str(p_id)
        timing = int(timing)

        info = {
            'time'      : unixtime,
            'timing'    : timing,
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


        @check_sign(sign)
        def is_sign(): pass
     
        if not is_sign:
            info['err_msg'] = 'sign err'
            return self.write(ret_json(info))

        ''' 
            unquote(p_name) is unicode str 
        '''
        if unquote(p_name) != game_info[p_id]['name']:
            info['err_msg'] = 'region name err'
            return self.write(ret_json(info))

        if not game_info.has_key(p_id):
            info['err_msg'] = 'p_id err'
            return self.write(ret_json(info))

        if not list_url or not oss2_task_id or u_type not in ['hot','stop','pre_hot','pre_stop']:
            info['err_msg'] = 'list_url or u_type or oss2_task_id err'
            return self.write(ret_json(info))

        if timing == 1 and time.time() > int(unixtime):
            info['err_msg'] = 'time is too small'
            return self.write(ret_json(info))
        elif timing == 0 and int(unixtime) > 0:
            info['err_msg'] = 'timing is 0, not need time arg'
            return self.write(ret_json(info))


        if game_info[p_id][u_type]:
            '''   消息Push
            '''
            info['success'] = 1
            publish(ret_json(info))
            return self.write(ret_json(info))
        else:
            info['err_msg'] = 'invalid msg'
            return self.write(ret_json(info))


# get redis
class get_done_task_list(tornado.web.RequestHandler):
    def get(self):
        sign     = self.get_argument('sign' ,0)

        @check_sign(sign)
        def is_sign(): pass

        if not is_sign: 
            return self.write(ret_json({'success':-1}))

        task_result_set = []
        for task_id in task_id_sortset:
            r = get_task_result(task_id)
            r and task_result_set.append(r)

        try:
            task_result_set = sorted(
            task_result_set,
            key=lambda x: int(x['start_time']),
            reverse=True
            )
        except:
            pass

        task_result_set = task_result_set[0:15]
        return self.write(ret_json(task_result_set))


class get_actives_task_list(tornado.web.RequestHandler):
    def get(self):
        sign     = self.get_argument('sign' ,0)

        @check_sign(sign)
        def is_sign(): pass
            
        if not is_sign: 
            return self.write(ret_json({'success':-1}))

        active_task_list = get_active_task_list()
        if active_task_list:
            self.write(ret_json(active_task_list))
        else:
            self.write({'success':-1})


class get_task_results(tornado.web.RequestHandler):
    def get(self,task_id):
        sign     = self.get_argument('sign' ,0)

        @check_sign(sign)
        def is_sign(): pass
            
        if not is_sign: 
            return self.write(ret_json({'success':-1}))

        result = get_task_result(task_id)

        if result:
            self.write('%s'%result)
        else:
            self.write({'success':-1})

class delete_task_result(tornado.web.RequestHandler):
    def get(self,task_id):    
        sign     = self.get_argument('sign' ,0)

        @check_sign(sign)
        def is_sign(): pass
            
        if not is_sign: 
            return self.write(ret_json({'success':-1}))

        try:
            revoke_task(task_id)
            info = {'success':1}
        except:
            print traceback.print_exc()
            info = {'success':-1}
        self.write(info)


class index_page(tornado.web.RequestHandler):
    def get(self):
        self.write(
            '<a href="/done_task/"> done_task</a>\n'
            '<a href="/active_task/"> active_task</a>'
            '<a href=""> </a> '
        )

application = tornado.web.Application([
    (r"/",                  index_page            ),
#    (r"/untime_send_msg",   untime_send_msg       ),
    (r"/time_send_msg",     time_send_msg         ),
    (r"/done_task/",        get_done_task_list    ),
    (r"/active_task/",      get_actives_task_list ),
    (r"/result_task/(\S+)", get_task_results      ),
    (r"/delete_task/(\S+)", delete_task_result    ),
], **settings)

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
