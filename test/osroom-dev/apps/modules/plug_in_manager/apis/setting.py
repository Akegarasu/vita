#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request

from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.login_manager import osr_login_required
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.plug_in_manager.process.setting import get_plugin_setting, update_plugin_setting, \
    refresh_plugin_setting, install_require_package


@api.route('/admin/plugin/setting', methods=['GET', "POST", "PUT"])
@osr_login_required
@permission_required()
def api_adm_plugin_setting():
    """
    插件设置
    GET:
        获取插件设置

        plugin_name:<str>, 插件名
    POST:
        刷新当前插件配置(当插件配置代码被修改后,如果未重新激活，系统保存的配置是不会更新的，所有可以使用此方法刷新)
        plugin_name:<str>, 插件名
    PUT:
        修改设置
        plugin_name:<str>, 插件名
        key:<str>,KEY
        value:<可多种类型的数据>, 值
    :return:
    """
    if request.c_method == "GET":
        data = get_plugin_setting()
    elif request.c_method == "POST":
        data = refresh_plugin_setting()
    elif request.c_method == "PUT":
        data = update_plugin_setting()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)


@api.route('/admin/plugin/setting/install-requirement', methods=["PUT"])
@osr_login_required
@permission_required()
def api_adm_install_requs():
    """
    插件需求包安装
    PUT:
        插件需求包安装
        plugin_name:<str>, 插件名

    :return:
    """
    if request.c_method == "PUT":
        data = install_require_package()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
