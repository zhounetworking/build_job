#!/usr/bin/python
#-*- coding:utf8 -*-
#
#

import os
import json
import logging
import smtplib, mimetypes
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
from email.mime.image import MIMEImage

from conf.config import *


# pub/sub daemon_getmsg.py ， 接收到的数据要以 ',' 分隔 , 只接收两个字段
def msg_parse(msg):
	msg_list = msg.split(',')
	if len(msg_list) != 2:
		pass

def Mail(user,passwd,mail_to,smtp_server, subject,mail_text,attachment="",charset="utf8"):
	msg 			= MIMEMultipart()
	msg['From'] 	= user
	msg['To'] 		= ';'.join(mail_to)
	msg['Subject']	= subject
   
	txt = MIMEText(mail_text, _charset=charset)
	msg.attach(txt)

	# add attachment of binary
	if attachment: 
		fileName = r'%s'%attachment
		ctype, encoding = mimetypes.guess_type(fileName)
		if ctype is None or encoding is not None:
			ctype = 'application/octet-stream'
		maintype, subtype = ctype.split('/', 1)

		attach = MIMEImage(
				(lambda f: (f.read(), f.close()))(open(fileName, 'rb'))[0], 
				_subtype = subtype
		)

		attach.add_header('Content-Disposition', 'attachment', filename = fileName)
		msg.attach(attach)
   
	# send mail
	try:
		smtp = smtplib.SMTP()  
		smtp.connect( smtp_server )  
		#smtp.login('papasg_report', passwd )  
		smtp.login(user, passwd )  
		smtp.sendmail(user, mail_to, msg.as_string())  
		smtp.quit()
		return True
	except:
		print('Fail')
		import traceback
		traceback.print_exc()
		return False


def init_logger():
	# create logger with 'control'
	logger = logging.getLogger('hrg_game')
	logger.setLevel(logging.INFO)

	# create file handler
	fh = logging.FileHandler(os.path.join(basedir, 'logs/update.log'))
	fh.setLevel(logging.INFO)

	# create console handler
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)

	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)

	# add the handlers to the logger
	logger.addHandler(fh)
	logger.addHandler(ch)

	return logger


# when do loop in function , init_logger will be initialized 4 times
log = init_logger()

def notification(job_result):
    result = (
        job_result['stat'] ,
        job_result['next_no'],
        job_result['job_name'],
        job_result['run_time'],
        json.dumps(job_result['error']) ,
        json.dumps(job_result['params']) ,
    )

    print('status:%s id:%s name:%s time:%s  job_error:%s job_params:%s'%result)

    stat = Mail(
        papasg_user,
        papasg_passwd,
        mail_to,
        smtp_server,
        subject,
        mail_text % result
    )

    return stat


if __name__ == '__main__':
	from config import *

	basedir = os.path.dirname(
    	os.path.abspath(os.path.dirname(__file__))
	)
	
	log = init_logger()
	stat = Mail(papasg_user,papasg_passwd,mail_to,smtp_server,subject,'版本更新完毕, 请线上验证')

	if stat:
		log.info('mail send SUCCESS')
	else:
		log.error('mail send FAILURE')
