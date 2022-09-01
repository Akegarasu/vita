#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.core.plug_in.manager import plugin_manager


def reader_city(ip):
    """
    :param reader_obj: reader object
    :param ip:
    :return:a dict
    """

    # 检测插件
    data = plugin_manager.call_plug(hook_name="ip_geo",
                                    ip=ip)

    if data == "__no_plugin__":
        return {}
    return data
