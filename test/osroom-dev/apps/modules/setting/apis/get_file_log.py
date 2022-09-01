#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.core.flask.login_manager import osr_login_required
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.setting.process.get_file_log import sys_log



@api.route('/admin/setting/sys/log', methods=['GET'])
@osr_login_required
@permission_required()
def api_sys_log():
    """
    GET:
        获取文件日志
        name:<str>,日志名称
        ip:<str>,要获取哪个主机的日志
        page:<int>
        :return:
    """
    data = sys_log()
    return response_format(data)
