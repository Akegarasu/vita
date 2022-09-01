#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from functools import wraps
from multiprocessing import Process
import threading
"""
decorators
"""


def async_thread(timeout=None):

    def decorator(f):
        """
        multiprocessing Process
        :return:
        """

        @wraps(f)
        def wrapper(*args, **kwargs):
            t = threading.Thread(target=f, args=args, kwargs=kwargs)
            t.start()
            if timeout:
                t.join(timeout=timeout)
        return wrapper
    return decorator


def async_process(timeout=None):
    def decorator(f):
        """
        multiprocessing Process
        :return:
        """
        @wraps(f)
        def wrapper(*args, **kwargs):
            thr = Process(target=f, args=args, kwargs=kwargs)
            thr.start()
            if timeout:
                thr.join(timeout=timeout)
        return wrapper

    return decorator

