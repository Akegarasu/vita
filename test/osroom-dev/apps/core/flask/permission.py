#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask_babel import gettext
from flask_login import current_user
from functools import wraps
from flask import request, abort
from werkzeug.utils import redirect
from apps.app import cache, mdbs
from apps.configs.sys_config import GET_DEFAULT_SYS_PER_CACHE_KEY, GET_ALL_PERS_CACHE_KEY
from apps.core.flask.response import response_format
from apps.core.utils.get_config import get_config

__author__ = 'woo'
"""
decorators
"""


def permission_required(use_default=True):
    """
    权限验证
    :param use_default:
    :return:
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            custom_per = custom_url_permissions()
            if custom_per:
                # 验证api自定义的权限
                r = current_user.can(custom_per)
                keys = " or ".join(get_permission_key(custom_per))
            elif use_default:
                # 验证默认指定的通用权限
                per = get_permissions_default()
                r = current_user.can(per)
                keys = " or ".join(get_permission_key(per))
            else:
                r = True
            if not r:
                return response_format({"msg": gettext('Permission denied,requires "{}" permission').format(
                    keys), "msg_type": "w", "custom_status": 401})
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# page url permission required
def page_permission_required():
    """
    页面路由权限验证
    :return:
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            custom_login_required = custom_url_login_auth()
            if custom_login_required and current_user.is_anonymous:
                return redirect(get_config("login_manager", "LOGIN_VIEW"))
            custom_per = custom_url_permissions()
            if custom_per:
                r = current_user.can(custom_per)
                if not r:
                    abort(401)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def adm_page_permission_required():
    """
    页面路由权限验证
    :return:
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            custom_login_required = custom_url_login_auth()
            if custom_login_required and current_user.is_anonymous:
                return redirect(get_config("login_manager", "LOGIN_VIEW"))
            custom_per = custom_url_permissions()
            if custom_per:
                r = current_user.can(custom_per)
                if not r:
                    abort(401)
            else:
                staff_per = get_permission("STAFF")
                r = current_user.can(staff_per)
                if not r:
                    abort(401)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

@cache.cached(
    timeout=3600,
    key_base64=False,
    key=GET_DEFAULT_SYS_PER_CACHE_KEY,
    db_type="redis")
def get_permissions_default():
    """
    获取所有权限值,并相"|"
    :return:
    """
    query = {"value": {"$exists": True}, "is_default": 1}
    pers = mdbs["user"].dbs["permission"].find(query)
    value = 0b0
    for per in pers:
        value = value | per["value"]
    return value


@cache.cached(
    timeout=3600,
    key_base64=False,
    key=GET_ALL_PERS_CACHE_KEY,
    db_type="redis")
def get_permissions():
    """
    获取所有权限

    :return:{name:<value>}
    """
    query = {"value": {"$exists": True}}
    pers = mdbs["user"].dbs["permission"].find(query)
    value = {}
    for per in pers:
        value[per["name"]] = per["value"]
    return value


def get_permission(name):
    """
    获取一个权限值
    :return:
    """
    pers = get_permissions()
    if name in pers:
        value = pers[name]
    else:
        value = 0
    return value


def get_permission_key(permission):
    """
    获取一个权限包括了那些权限, 返回他们的key
    :param permission:
    :return:
    """
    keys = []
    for k, v in get_permissions().items():
        if int(v) & int(permission):
            keys.append(k)

    return keys


def custom_url_permissions(url=None, method="GET"):
    """
    获取自定义权限
    :return:
    """
    if not url:
        url = request.path
        method = request.c_method

    url_per = get_sys_url(url=url.rstrip("/"))
    if url_per and method in url_per["custom_permission"]:
        return url_per["custom_permission"][method]


def custom_url_login_auth(url=None, method="GET"):
    """
    获取自定义权限
    :return:
    """
    if not url:
        url = request.path
        method = request.c_method

    url_per = get_sys_url(url=url.rstrip("/"))
    if url_per and url_per["type"] != "page" and method in url_per["login_auth"]:
        return url_per["login_auth"][method]


@cache.cached(timeout=3600, key_base64=False, db_type="redis")
def get_sys_url(url):
    """
    获取url权限等信息
    :param url:
    :return:
    """
    value = mdbs["sys"].db.sys_urls.find_one({"url": url}, {"_id": 0})
    return value
