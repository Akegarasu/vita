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
from apps.modules.plug_in_manager.process.manager import start_plugin, stop_plugin, get_plugins, delete_plugin, \
    upload_plugin


@api.route('/admin/plugin', methods=['GET', 'POST', "PUT", "DELETE"])
@osr_login_required
@permission_required()
def api_adm_plugin():
    """
    插件管理
    GET:
        获取所有插件
        page:<int>,第几页, 默认1
        pre:<int>,每页个数, 默认10
        keyword:<str>, 搜索用

    POST:
        插件安装
        upfile:<file>,上传的插件压缩包
    PUT:
        操作插件
        action:<str>, start:激活插件 stop:停用插件
        name:<str>, 插件名称
    :return:
    """
    if request.c_method == "GET":
        data = get_plugins()
    elif request.c_method == "POST":
        data = upload_plugin()
    elif request.c_method == "PUT":
        if request.argget.all('action') == "start":
            data = start_plugin()
        else:
            data = stop_plugin()
    elif request.c_method == "DELETE":
        data = delete_plugin()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
