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
from apps.modules.theme_setting.process.page import add_page, delete_page


@api.route('/admin/theme/page', methods=['GET', 'POST', "PUT", "DELETE"])
@osr_login_required
@permission_required()
def api_add_page():
    """
    POST:
        添加页面
        routing:<str>,路由
        content:<str>, 内容
    DELETE:
        删除自己添加的页面
        file_path:<str>,页面html文件所在目录
        filename:<str>,页面html文件名

    """

    if request.c_method == "POST":
        data = add_page()
    elif request.c_method == "DELETE":
        data = delete_page()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
