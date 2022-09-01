#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2020/1/7
# @Author : Allen Woo
from urllib.parse import quote
# from celery.schedules import crontab
from apps.configs.db_config import DB_CONFIG


class CeleryConfig:

    connection_mode = "redis"
    redis_configs = []
    if connection_mode == "redis":
        redis_configs = [{
            "host":  DB_CONFIG["redis"]["host"][0],
            "port":  DB_CONFIG["redis"]["port"][0],
            "password": DB_CONFIG["redis"]["password"]
        }]
        # redis_configs = DB_CONFIG["redis"][0:1]
    elif connection_mode == "sentinel":
        redis_configs = DB_CONFIG["redis"][:]

    BROKER_URL = '{}://'.format(connection_mode)
    for conf in redis_configs:
        BROKER_URL = "{celery_redis_uri}:{password}@{hostname}:{port},".format(
            celery_redis_uri=BROKER_URL,
            password=quote(conf["password"]),
            hostname=conf["host"],
            port=conf["port"]
        )
    BROKER_URL = "{}".format(BROKER_URL.strip(","))

    # celery_once: No need to escape(quote) password
    ONCE_BROKER_URL = '{}://'.format(connection_mode)
    for conf in redis_configs:
        ONCE_BROKER_URL = "{celery_redis_uri}:{password}@{hostname}:{port},".format(
            celery_redis_uri=ONCE_BROKER_URL,
            password=conf["password"],
            hostname=conf["host"],
            port=conf["port"]
        )

    ONCE_BROKER_URL = "{}".format(ONCE_BROKER_URL.strip(","))

    RESULT_BACKEND = BROKER_URL
    TASK_TIME_LIMIT = 60 * 7
    TASK_SOFT_TIME_LIMIT = 60 * 5

    CELERY_IGNORE_RESULT = False
    RESULT_EXPIRES = 3600 * 12
    CELERYD_MAX_TASKS_PER_CHILD = 100
    CELERY_EVENT_QUEUE_TTL = 10
    # BROKER_CONNECTION_TIMEOUT = 4
    WORKER_CONCURRENCY = 1
    WORKER_PREFETCH_MULTIPLIER = 1
    RESULT_EXPIRES = 3600 * 12

    # 定时任务
    # CELERYBEAT_SCHEDULE = {}
