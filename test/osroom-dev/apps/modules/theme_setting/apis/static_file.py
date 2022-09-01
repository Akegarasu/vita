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
from apps.modules.theme_setting.process.static_file import get_static_file_content, edit_static_file, get_static_files


@api.route('/admin/static/file', methods=['GET', 'POST', "PUT", "DELETE"])
@osr_login_required
@permission_required()
def api_static_file():
    """
    GET:
        1.获取静态文件内容
        file_path:<str>,静态文件所在目录
        filename:<str>,文件名

        2.获取静态文件名列表
        page:<int>, 第几页, 默认1
        pre:<int>, 第几页, 默认15
        keyword:<str>,关键词搜索用
        type:<str>, "all" or "default" or "custom"

    PUT:
        编辑静态文件内容
        file_path:<str>,静态文件所在目录
        filename:<str>,文件名
        content:<str>, 内容
    """

    if request.c_method == "GET":
        if request.argget.all("filename"):
            data = get_static_file_content()
        else:
            data = get_static_files()

    elif request.c_method == "PUT":
        data = edit_static_file()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
