#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2020/03/16 17:58
# @Author : Allen Woo
from redis import ConnectionPool, StrictRedis


class Myredis:

    def __init__(self, host, port, password, use_pool=True):

        self.db_configs = None
        self.host = host
        self.port = port
        self.password = password
        self.use_pool = use_pool

    def init_app(self):

        # redis init
        if self.use_pool:
            redis_pool = ConnectionPool(
                host=self.host,
                port=self.port,
                password=self.password)
            redis = StrictRedis(
                connection_pool=redis_pool
            )
        else:
            redis = StrictRedis(
                host=self.host,
                port=self.port,
                password=self.password
            )

        for op in redis.__class__.__dict__.keys():
            if op.startswith("_"):
                continue
            self.__dict__[op] = getattr(redis, op)
