#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import base64
from functools import wraps
import time
from flask import current_app, request
from apps.utils.format.obj_format import json_to_pyseq, pyseq_to_json


class Cache:

    """
    缓存模块
    """

    def __init__(self, app=None):
        self.cache_none = type(CacheNone())
        self.cache_none_obj = CacheNone()
        if app is not None:
            self.init_app(app)
        self.redis_exists_exception = False

    def init_app(self, app, **kwargs):

        self.app = app
        self._get_interface(app)

    def _get_interface(self, app):

        self.config = app.config.copy()
        self.config.setdefault('CACHE_DEFAULT_TIMEOUT', 300)
        self.config.setdefault('CACHE_REDIS', None)
        self.config.setdefault('CACHE_MONGODB_DBS', None)
        self.config.setdefault('CACHE_MONGODB_COLLECT', "osr_cache")
        self.config.setdefault('CACHE_KEY_PREFIX', 'osr-cache:')
        self.config.setdefault('CACHE_TYPE', 'redis')
        self.config.setdefault('USE_CACHE', True)

        # 需要配置好redis和mongodb, 系统对不同的数据的缓存需要不一样的数据库保存
        if self.config["CACHE_REDIS"]:
            self.redis = self.config["CACHE_REDIS"]
        else:
            raise Exception('Missing configuration "CACHE_REDIS"')

        if self.config["CACHE_MONGODB_DBS"]:
            self.mdb_coll = self.config["CACHE_MONGODB_DBS"][self.config["CACHE_MONGODB_COLLECT"]]
        else:
            raise Exception('Missing configuration "CACHE_MONGODB"')

    @property
    def cache(self):
        app = self.app or current_app
        return app.extensions['cache'][self]

    def cached(self, timeout=None, key=None, key_base64=True, db_type=None, key_prefix="", is_class_func=False):
        """
        设置缓存
        :param timeout:缓存保存时间
        :param key: 默认使用func的参数拼接作为key, 没有参数则使用为'osr/{}'.format(request.path)
        :param key_base64: 当key==None时生效.默认使用base64编码key.
                           key_base64为False, 则不编码key
        :param db_type: 不使用系统设置的db type时指定类型mongodb或redis
        :return:
        """

        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.config['USE_CACHE']:
                    # 不使用缓存
                    return f(*args, **kwargs)

                cache_key = self._create_cache_key(key=key,
                                                   key_prefix=key_prefix,
                                                   key_base64=key_base64,
                                                   fun_name=f.__name__,
                                                   args=args,
                                                   kwargs=kwargs,
                                                   is_class_func=is_class_func)
                func_result = self.get(key=cache_key, db_type=db_type)
                if func_result != self.cache_none:
                    return func_result
                else:
                    func_result = f(*args, **kwargs)
                    self.set(
                        cache_key,
                        func_result,
                        ex=timeout,
                        db_type=db_type)
                    return func_result
            return decorated_function

        return decorator

    def _create_cache_key(self, key, key_prefix, key_base64, fun_name, args, kwargs, is_class_func, key_regex=False):
        """
        :param key:
        :param key_prefix:
        :param key_base64:
        :param fun_name:
        :param args:
        :param kwargs:
        :param is_class_func:
        :param key_regex: 当delete函数调用时可以使用该参数,用于生成正则匹配的cache_key
        :return:
        """
        if key_regex:
            key_rule = ".*"
        else:
            key_rule = ""
        if key is None:
            tkey = "F-{}".format(fun_name)
            if is_class_func:
                targs = args[1:]
            else:
                targs = args[:]

            if targs or kwargs:
                for arg in targs:
                    tkey = "{}_{}".format(tkey, str(arg))
                tkwargs = sorted(kwargs.items(), key=lambda x: x[0])
                for arg in tkwargs:
                    tkey = "{}{}_{}_{}".format(
                        tkey, key_rule, arg[0], str(arg[1]))

                cache_key = tkey.lstrip("_")
            else:
                if request:
                    cache_key = "{}_{}".format(tkey, request.path)
                else:
                    cache_key = ""
            cache_key = "{}_{}".format(key_prefix, cache_key)
            if key_base64:
                cache_key = base64.b64encode(cache_key.encode()).decode()
        else:
            cache_key = key

        return cache_key

    def get(self, key, db_type=None):
        """
        获取一个cache
        :param key:
        :param db_type: 不使用系统设置的db type时指定类型mongodb或redis
        :return:default:获取不到时返回
        """

        key = "{}{}".format(self.config['CACHE_KEY_PREFIX'], key)
        if (db_type == "redis" or (not db_type and self.config["CACHE_TYPE"] == "redis")) \
                and not self.redis_exists_exception:
            value = self.redis.get(key)
            if value:
                value = value.decode("utf-8")
                if value == self.cache_none_obj.value:
                    return None
                value = json_to_pyseq(value)
                return value
            # 防止value为None所以查询不到缓存时, 使用cache空类
            return self.cache_none

        elif db_type == "mongodb" or (not db_type and self.config["CACHE_TYPE"] == "mongodb") \
                or self.redis_exists_exception:

            value = self.mdb_coll.find_one({"key": key}, {"_id": 0})
            if value and value["expiration"] < time.time():
                # 已过期
                self.delete(key, db_type=db_type)
                return self.cache_none
            elif value:
                value["value"] = value["value"]
                if value["value"] == self.cache_none_obj.value:
                    return None
                value = json_to_pyseq(value["value"])
                return value

            # 防止value为None时, 所以查询不到缓存时, 使用cache空类
            return self.cache_none

    def set(self, key, value, ex=None, db_type=None):
        """
        设置一个cache
        :param key:
        :param value:
        :param db_type: 不使用系统设置的db type时指定类型mongodb或redis
        :return:ex,如果ex为0表示
        """

        key = "{}{}".format(self.config['CACHE_KEY_PREFIX'], key)
        if ex is None:
            ex = self.config["CACHE_DEFAULT_TIMEOUT"]

        if (db_type == "redis" or (not db_type and self.config["CACHE_TYPE"] == "redis")) \
                and not self.redis_exists_exception:
            json_value = pyseq_to_json(value)
            try:
                if json_value is None:
                    json_value = self.cache_none_obj.value
                self.redis.set(key, json_value, ex=ex)
                self.redis_exists_exception = False
            except Exception as e:
                self.redis_exists_exception = True
                print(key)
                print(e)
                print("ERROR: Redis error")

            return value

        elif db_type == "mongodb" or (not db_type and self.config["CACHE_TYPE"] == "mongodb")\
                or self.redis_exists_exception:
            json_value = pyseq_to_json(value)
            r = self.mdb_coll.update_one(
                {"key": key},
                {"$set": {"value": json_value, "expiration": time.time() + ex}},
                upsert=True)
            if r.modified_count:
                return value

            elif not r.modified_count and not r.matched_count:
                return value
            else:
                return None

    def delete(self, key, db_type=None, key_regex=False):
        """
        删除cache
        :param db_type: 不使用系统设置的db_type时, 请指定类型mongodb或redis
        :param key_regex:默认关闭正则匹配key,
        :return:
        """
        key = "{}{}".format(self.config['CACHE_KEY_PREFIX'], key)

        if (db_type == "redis" or (not db_type and self.config["CACHE_TYPE"] == "redis")) \
                and not self.redis_exists_exception:
            try:
                if key_regex:
                    if ".*" in key:
                        key = key.replace(".*", "*")
                    else:
                        key = "*{}*".format(key)
                    keys = self.redis.keys(pattern=key)
                    for key in keys:
                        self.redis.delete(key.decode())
                else:
                    self.redis.delete(key)
                self.redis_exists_exception = False
            except Exception:
                self.redis_exists_exception = True
        elif db_type == "mongodb" or (not db_type and self.config["CACHE_TYPE"] == "mongodb")\
                or self.redis_exists_exception:
            if key_regex:
                q = {"key": {"$regex": key}}
            else:
                q = {"key": key}
            self.mdb_coll.delete_many(q, regular_escape=False)

    def delete_autokey(
            self,
            fun,
            key_base64=None,
            key_prefix="",
            db_type=None,
            key_regex=False,
            *args,
            **kwargs):
        """
        删除自动生成key的cache
        :param fun: 使用缓存的函数
        :param key_base64:
        :param key_prefix:
        :param db_type:
        :param key_regex
        :param args:　使用缓存的函数的参数
        :param kwargs:　使用缓存的函数的参数
        :return:
        """
        if not isinstance(fun, str):
            fun = fun.__name__

        cache_key = self._create_cache_key(key=None,
                                           key_prefix=key_prefix,
                                           key_base64=key_base64,
                                           fun_name=fun,
                                           args=args,
                                           kwargs=kwargs,
                                           is_class_func=False,
                                           key_regex=key_regex)
        self.delete(key=cache_key, db_type=db_type, key_regex=key_regex)

    def get_autokey(
            self,
            fun,
            key_base64=None,
            key_prefix="",
            db_type=None,
            key_regex=False,
            *args,
            **kwargs):
        """
        生成一个调用方式的key
        :param fun: 使用缓存的函数
        :param key_base64:
        :param key_prefix:
        :param db_type:
        :param args:　使用缓存的函数的参数
        :param kwargs:　使用缓存的函数的参数
        :param kwargs:　使用缓存的函数的参数
        :return:
        """
        if not isinstance(fun, str):
            fun = fun.__name__

        cache_key = self._create_cache_key(key=None,
                                           key_prefix=key_prefix,
                                           key_base64=key_base64,
                                           fun_name=fun,
                                           args=args,
                                           kwargs=kwargs,
                                           is_class_func=False,
                                           key_regex=key_regex)
        return cache_key

    def clear(self, db_type=None):
        """
        清除所有的cache
        :param db_type: 不使用系统设置的db type时指定类型mongodb或redis
        :return:
        """
        if not db_type:
            if self.config["CACHE_TYPE"] == "redis":
                self.redis.delete(*self.redis.keys())
            else:
                self.mdb_coll.delete_many({})
        elif db_type:
            if db_type == "redis":
                self.redis.delete(*self.redis.keys())

            elif db_type == "mongodb":
                self.mdb_coll.delete_many({})


class CacheNone:

    """
    Cache None对象
    """

    def __init__(self):
        pass

    value = "OSR_Cache_None"

    def __str__(self):
        return self.value

