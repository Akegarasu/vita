#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import Response, jsonify


class OsrResponse(Response):
    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(OsrResponse, cls).force_type(rv, environ)


def response_format(data, status=200):
    """
    :param data:
    :param status:http status
    :return:
    """

    if not isinstance(data, dict):
        return data, status
    if "custom_status" not in data.keys():
        return data, status
    # custom_status 系统内部状态码
    # 401是无权访问, 405表示该请求方式不存在
    if data["custom_status"] in [400, 402, 403, 404, 422]:
        status = 200
    elif "http_status" in data:
        status = data["http_status"]
    else:
        status = data["custom_status"]
    return data, status
