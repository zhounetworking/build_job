# build_job
build job on jenkins


 工具需要启动三个组件
=====================

        * tools/start_celery.sh , celery 异步任务执行框架

        * api_web.py                    , restful api

        * daemon_getmsg.py              , 基于 redis pub/sub , 消息接收 daemon



 工具使用
=====================

        * http://127.0.0.1:8080/send_msg/task_name

        * http://127.0.0.1:8080/active_task/

        * http://127.0.0.1:8080/delete_task/

        * http://127.0.0.1:8080/result_task/

        * http://127.0.0.1:8080/done_task/


 使用 supervisor 管理
======================

        * pip install supervisor

        * cp -r tools/supervisor /etc/supervisor

        * /usr/local/bin/supervisord -c /etc/supervisor/supervisord.conf 
