#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from apps.core.flask.login_manager import osr_login_required

from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format

from apps.modules.setting.process.settings import sys_config_version, conf_version_switch, get_sys_configs, \
    sys_config_edit


@api.route('/admin/setting/sys/config/version', methods=['GET', 'PUT'])
@osr_login_required
@permission_required()
def api_sys_config_version():
    """
    GET:
        获取所有的系统配置版本, 和网站服务器主机
    PUT:
        切换单个节点网站的配置版本
        switch_version:<str>, 需要切换的版本号
        diable_update:<int> , 0 or 1
        host_ip:<str>, 主机ip

    :return:
    """
    if request.c_method == "GET":
        data = sys_config_version()
    elif request.c_method == "PUT":
        data = conf_version_switch()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)


@api.route('/admin/setting/sys/config', methods=['GET', 'PUT'])
@osr_login_required
@permission_required()
def api_sys_config():
    """
    GET:
        根据project获取当前最新配置(特殊配置将不会返回,如不允许再页面编辑的,即那些不带有"__restart__"key的)
        project:<array>, 能同时获取多个project的数据.不使用此参数则表示获取全部配置
        keyword:<str>, 搜索匹配关键字的结构
        only_project_field:<int>, 只需要project字段. 0 or 1.默认为0
    PUT:
        key:<str>, 要设置的配制参数的key
        project:<str>, 项目,比如这个key是comment下的，则project为comment
        value:<str or int or bool or list or dict or tuple>, key对应的值
        info:<str>, 说明

    :return:
    """
    if request.c_method == "GET":
        data = get_sys_configs()
    elif request.c_method == "PUT":
        data = sys_config_edit()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
