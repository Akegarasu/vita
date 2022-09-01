#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask_babel import gettext
import regex as re


class ArgVerify:

    def required(self, **kwargs):
        for reqarg in kwargs.get("reqargs"):
            if not reqarg[1]:
                data = {'msg': gettext('The "{}" cannot be empty').format(
                    reqarg[0]), 'msg_type': "w", "custom_status": 422}
                return False, data
        return True, None

    def min_len(self, **kwargs):

        vr = kwargs.get("vr")
        for reqarg in kwargs.get("reqargs"):
            if len(reqarg[1]) < vr:
                data = {'msg': gettext('The minimum length of "{}" is {} characters').format(
                    reqarg[0], vr), 'msg_type': "w", "custom_status": 422}
                return False, data
        return True, None

    def max_len(self, **kwargs):

        vr = kwargs.get("vr")
        for reqarg in kwargs.get("reqargs"):
            if len(reqarg[1]) > vr:
                data = {'msg': gettext('The maximum length of "{}" is {} characters').format(
                    reqarg[0], vr), 'msg_type': "w", "custom_status": 422}
                return False, data
        return True, None

    def need_type(self, **kwargs):

        vr = kwargs.get("vr")
        for reqarg in kwargs.get("reqargs"):
            if not isinstance(reqarg[1], vr):
                data = {'msg': gettext('"{}" needs to be of type {}').format(
                    reqarg[0], vr.__name__), 'msg_type': "w", "custom_status": 422}
                return False, data
        return True, None

    def only(self, **kwargs):
        vr = kwargs.get("vr")
        for reqarg in kwargs.get("reqargs"):
            if not reqarg[1] in kwargs.get("vr"):
                data = {
                    'msg': gettext('The value of parameter "{}" can only be one of "{}"').format(
                        reqarg[0],
                        ",".join(vr)),
                    'msg_type': "w",
                    "custom_status": 422}
                return False, data
        return True, None

    def can_not(self, **kwargs):
        vr = kwargs.get("vr")
        for reqarg in kwargs.get("reqargs"):
            if reqarg[1] in vr:
                data = {'msg': gettext('The value of parameter "{}" can not be "{}"').format(
                    reqarg[0], ",".join(vr)), 'msg_type': "w", "custom_status": 422}
                return False, data
        return True, None

    def allowed_type(self, **kwargs):
        vr = kwargs.get("vr")
        for reqarg in kwargs.get("reqargs"):
            if type(reqarg[1]) not in vr:
                data = {
                    'msg': gettext('Parameter {} can only be of the following type: "{}"').format(
                        reqarg[0],
                        ",".join(vr)),
                    'msg_type': 'error',
                    "custom_status": 422}
                return False, data
        return True, None

    def regex_rule(self, **kwargs):

        vr = kwargs.get("vr")
        if vr["is_match"]:
            for reqarg in kwargs.get("reqargs"):
                if not re.search(vr["rule"], reqarg[1]):
                    return False, {
                        'msg': gettext('The value of parameter "{}" is illegal').format(
                            reqarg[0]), 'msg_type': "w", "custom_status": 422}

        else:
            for reqarg in kwargs.get("reqargs"):
                if re.search(vr["rule"], reqarg[1]):
                    return False, {
                        'msg': gettext('The value of parameter "{}" is illegal').format(
                            reqarg[0]), 'msg_type': "w", "custom_status": 422}

        return True, None


arg_ver = ArgVerify()


def arg_verify(reqargs=[], **kwargs):
    """
    :param reqargs:数组，如：[(arg_key, arg_value)]
    :param required:bool,  为True表示不能为空
    :param min_len: int, 最小长度
    :param max_len: int, 最大长度
    :param need_type: 类型如int, dict, list .tuple
    :param only: 数组, 只能是only数组中的元素
    :param can_not: 数组, 不能是can_not中的元素
    :param allowed_type: 数组, 允许数据的类型是allowed_type中的元素
    :param regex_rule: Such as::{"rule":r".*", "is_match":True}
                        is_match ：True 表示需要匹配成功, False 表示需要不匹配该规则的
    :param args:
    :param kwargs:
    :return:验证状态,验证信息
    """
    for k, v in kwargs.items():
        s, r = getattr(arg_ver, k)(reqargs=reqargs, vr=v)
        if not s:
            return s, r
    return True, None
