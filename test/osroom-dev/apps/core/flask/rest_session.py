#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from uuid import uuid1
import time
from flask import request

from apps.utils.format.obj_format import json_to_pyseq


class RestSession:

    """
    区别与flask-session 针对Rest api请求的Session
    """

    def __init__(self):
        self.sid = None

    def init_app(self, app, **kwargs):

        self._get_interface(app)
        @app.before_request
        def init_current_session_id():
            """
            请求前调用此函数设置当前请求的sid
            :return:
            """
            self.sid = "{}rest-{}".format(
                self.config["SESSION_KEY_PREFIX"], str(uuid1()))
            header = request.headers.get('OSR-ClientId')
            if header:
                self.sid = header

        @app.teardown_request
        def clear_current_session_id(e):
            """
            清理当前请求init_current_session中设置的sid
            :return:
            """
            self.sid = None

    def _get_interface(self, app):

        self.config = app.config.copy()
        self.config.setdefault('SESSION_TYPE', 'mongodb')
        self.config.setdefault('SESSION_PERMANENT', True)
        self.config.setdefault('SESSION_KEY_PREFIX', 'session:')
        self.config.setdefault('SESSION_REDIS', None)
        self.config.setdefault('SESSION_MONGODB', None)
        self.config.setdefault('SESSION_MONGODB_DB', 'osr_sys')
        self.config.setdefault('SESSION_MONGODB_COLLECT', 'osr_session')
        self.config.setdefault('SESSION_KEY_PREFIX', 'osr-session:')
        self.config.setdefault('PERMANENT_SESSION_LIFETIME', 86400 * 30)

        if self.config["SESSION_TYPE"] == "redis":
            if self.config["SESSION_REDIS"]:
                self.redis = self.config["SESSION_REDIS"]
            else:
                raise Exception('Missing configuration "SESSION_REDIS"')
        elif self.config["SESSION_TYPE"] == "mongodb":
            if self.config["SESSION_MONGODB"]:
                self.mdb_coll = self.config["SESSION_MONGODB"][self.config["SESSION_MONGODB_DB"]
                                                               ][self.config["SESSION_MONGODB_COLLECT"]]
            else:
                raise Exception('Missing configuration "SESSION_MONGODB"')

    def get(self, key=None, default=None):
        """
        获取一个session
        :param key:
        :return:default:获取不到时返回
        """
        if self.config["SESSION_TYPE"] == "redis":
            temp_value = self.redis.get(self.sid)
            if temp_value:
                temp_value = json_to_pyseq(temp_value.decode())
                if key and key in temp_value:
                    return temp_value[key]
                elif key:
                    return None
                else:
                    return temp_value

        else:
            query = {"id": self.sid}
            if key:
                query[key] = {"$exists": True}
                value = self.mdb_coll.find_one(query, {key: 1})
                if value:
                    return value[key]
            else:
                value = self.mdb_coll.find_one(query, {"_id": 0})
                if value:
                    return value
        return default

    def set(self, key, value):
        """
        设置一个sid的数据, 不存在则创建
        :param key:
        :param value:
        :return:
        """
        if self.sid:
            if self.config["SESSION_TYPE"] == "redis":

                temp_value = self.redis.get(self.sid)
                if temp_value:
                    temp_value = json_to_pyseq(temp_value.decode())
                    temp_value[key] = value
                else:
                    temp_value = {
                        key: value,
                        "expiration": time.time() +
                        self.config["PERMANENT_SESSION_LIFETIME"]}
                self.redis.set(self.sid, temp_value)
                return self.sid

            else:
                # mongodb
                r = self.mdb_coll.update_one(
                    {"id": self.sid}, {"$set": {key: value}}, upsert=True)

                if r.modified_count:
                    return self.sid

                elif not r.modified_count and not r.matched_count:
                    self.mdb_coll.update_one({"id": self.sid}, {"$set": {
                                             "expiration": time.time() + self.config["PERMANENT_SESSION_LIFETIME"]}})
                    return self.sid
                else:
                    return None
        return None

    def delete(self, key=None):
        """
        删除当前的session中的key
        :return:
        """

        if self.config["SESSION_TYPE"] == "redis":
            if key:
                temp_value = self.redis.get(self.sid)
                if temp_value:
                    temp_value = json_to_pyseq(temp_value.decode())
                    if key and key in temp_value:
                        del temp_value[key]
                        self.redis.set(self.sid, temp_value)
            else:
                self.redis.delete(self.sid)

        else:

            if key:
                se = self.mdb_coll.find_one({"id": self.sid})
                if se and key in se:
                    del se[key]
                    self.mdb_coll.update_one({"_id": se["_id"]}, {"$set": se})

            else:
                self.mdb_coll.delete_one({"id": self.sid})
