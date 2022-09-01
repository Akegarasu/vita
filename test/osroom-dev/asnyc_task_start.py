#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2020/03/14 13:45
# @Author : Allen Woo
import os
from apps.configs.sys_config import LOG_PATH


def async_task_worker():
    print(" * Asynchronous service: Celery worker starting...")
    try:
        shcmd = """ps -ef | grep celery_worker.celery | awk '{print $2}' | xargs kill -9"""
        os.system(shcmd)
        print("   Clean up legacy process successfully")
    except Exception as e:
        print(e)

    log_path = "{}/celery.log".format(LOG_PATH)
    # 异步任务定时器
    # celery_beat = "celery -A celery_worker.celery beat -l info --loglevel=debug " \
    #               "--logfile={logfile} >{logfile} 2>&1 &".format(
    #             logfile="{}/celery.log".format(LOG_PATH)
    # )
    # os.system(celery_beat)
    # 异步任务
    celery_worker = "celery -A celery_worker.celery worker --loglevel=debug --logfile={logfile} >{logfile} 2>&1 &".format(
        logfile=log_path
    )
    os.system(celery_worker)


if __name__ == "__main__":
    async_task_worker()
