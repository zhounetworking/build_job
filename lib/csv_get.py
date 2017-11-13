#!/usr/bin/python
#-*- coding:utf8 -*-


import urllib,os,shutil
import threadpool as tp

from socket import setdefaulttimeout

from lib.utils import log


class csv_download(object):
    def __init__(self,csv_list_url,csv_path):
        self.thread_num  = 10
        self.download_err= []
        self.csv_path    = csv_path
        csv_list = urllib.urlopen(csv_list_url)
        if csv_list.getcode() == 200:
            self.csv_list    = [ csv.strip() for csv in csv_list ]
        else:
            raise Exception,'activity url download err'

        log.info("activitylist: %s  num: %s"%(csv_list_url,len(self.csv_list)))

        # 清空本地csv目录
        if os.path.isdir(csv_path):
            shutil.rmtree(csv_path)
            os.makedirs(csv_path)
        else:
            os.makedirs(csv_path)

        # 下载超时 5s
        setdefaulttimeout(5)

    def download(self,csv_url): 
        try:
            csv_name = csv_url.split('/')[-1]
            csv_http_handler = urllib.urlopen(csv_url)
            if csv_http_handler.getcode() != 200:
                raise Exception
            csv_txt = csv_http_handler.read()
            csv_file = open('%s/%s'%(self.csv_path,csv_name),'w')
            csv_file.write(csv_txt)
            csv_file.close()
            log.info("download csv: %s"%csv_name)
        except Exception,e:
            self.download_err.append(csv_name)
            log.info("err csv url : %s"%csv_url)
            #print e


    def run(self):
        pool = tp.ThreadPool(self.thread_num)
        requests = tp.makeRequests(self.download,self.csv_list)

        try:
            [ pool.putRequest(req) for req in requests ]
            pool.wait()
        except:
            print 'thread pool err'

    def is_ok(self):
        return len(self.download_err) == 0

if __name__ == '__main__':
    url = 'http://hrgoss2.hrgame.com.cn/data/activity/3_4.3/2017-10-18/activity.list'
