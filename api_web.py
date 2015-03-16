#!/usr/bin/python
#-*- coding:utf8 -*-
#

import json
import time

import tornado.ioloop
import tornado.web

from lib.publish import *
from lib.Run import job_dict

from conf.redis_config import task_id_sortset

from task.manage_task import get_active_task_list ,get_task_result,revoke_task


settings = {'debug' : True}


# send msg to redis pub/sub, msg 数据解析就放在 web 层面吧 , lib.utils.msg_parse
# http://192.168.1.100:8080/send_msg?data=test2&time=1423749993
class send_msg(tornado.web.RequestHandler):
    def get(self,msg):
        info = {}

        try:
            arg = self.get_argument('time')
        except:
            arg = None

        info['data']  = msg
        info['time']  = arg

        if msg in job_dict:
            publish(msg)
            info['info'] = 1
            self.write(info)
        else:
            info['info'] = 0
            self.write(info)



class new_send_msg(tornado.web.RequestHandler):
    def get(self):
        unixtime = self.get_argument('time',0)
        msg      = self.get_argument('msg' ,0)
        
        info = {}
        info['msg']  = msg
        info['time'] = unixtime
        info['success'] = -1

        try:
            if time.time() > int(unixtime):
                info['err_msg'] = 'time is to small'
                return self.write(info)
        except:
            info['err_msg'] = 'bad time format'
            return self.write(info)

        if unixtime and msg:
            if msg in job_dict:
                data = msg + ',' + unixtime
                publish(data)
                info['success'] = 1
                return self.write("%s" % info)
            else:
                info['err_msg'] = 'invalid msg'
                return self.write(info)
        else:
            info['err_msg'] = 'no msg or no time'
            return self.write(info)


# get redis
class get_done_task_list(tornado.web.RequestHandler):
	def get(self):
		task_result_set = []
		for task_id in task_id_sortset:
			r = get_task_result(task_id)

			#if r:
			r and task_result_set.append(r)

		try:
			task_result_sort_set = sorted(
				task_result_set,
				key=lambda x:x['start_time'],
			)
		except:
			task_result_sort_set = task_result_set

		self.write('%s'% task_result_sort_set)
		#self.write('%s \n i %s i'% (task_result_sort_set,task_id_sortset))


class get_actives_task_list(tornado.web.RequestHandler):
	def get(self):
		active_task_list = get_active_task_list()
		if active_task_list:
			self.write('%s'%active_task_list)
		else:
			self.write({'info':1})


class get_task_results(tornado.web.RequestHandler):
	def get(self,task_id):
		result = get_task_result(task_id)

		if result:
			self.write('%s'%result)
		else:
			self.write({'info':1})

class delete_task_result(tornado.web.RequestHandler):
	def get(self,task_id):
		try:
			revoke_task(task_id)
			info = {'info':1}
		except:
			info = {'info':-1}
		self.write(info)


class index_page(tornado.web.RequestHandler):
	def get(self):
		self.write('<a href="/done_task/"> done_task</a>\n'
				   '<a href="/active_task/"> active_task</a>'
				   '<a href=""> </a> ')

application = tornado.web.Application([
    (r"/",					index_page				),
    (r"/send_msg/(\S+)", 	send_msg				),
    (r"/new_send_msg",		new_send_msg			),
    (r"/done_task/", 		get_done_task_list		),
    (r"/active_task/", 		get_actives_task_list	),
    (r"/result_task/(\S+)", get_task_results 		),
    (r"/delete_task/(\S+)", delete_task_result 		),
], **settings)

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
