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
from apps.modules.report.process.post_access import post_access



@api.route('/admin/post/access', methods=['GET'])
@osr_login_required
@permission_required()
def api_post_access():
    """
    GET:
        获取post数据统计
        days:<int>

    """
    if request.c_method == "GET":
        data = post_access()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
