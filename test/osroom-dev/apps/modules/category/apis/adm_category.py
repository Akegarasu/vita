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
from apps.modules.category.process.category import categorys, category_add, category_edit, \
    category_delete, get_category_type


@api.route('/admin/content/category', methods=['GET', 'POST', 'PUT', 'DELETE'])
@osr_login_required
@permission_required()
def api_adm_category():
    """
    Admin管理端category管理
    GET:
        1.获取指定的type的所有分类
        type:<str>, 你设置的那几个类别中的类别,在config.py文件中category, 或者网站管理设置

        2.获取所有的type
        get_type:<int>, get_type为1
    POST:
        添加文集
        name:<str>
        type:<str>, 只能是你设置的那几个类别,在config.py文件中category, 或者网站管理设置
    PUT:
        修改文集
        id:<str>, post category id
        name:<str>
    DELETE:
        删除文集名称
        ids:<array>, post category ids
    """

    if request.c_method == "GET":
        if not request.argget.all("get_type"):
            data = categorys(0)
        else:
            data = get_category_type()

    elif request.c_method == "POST":
        data = category_add(0)
    elif request.c_method == "PUT":
        data = category_edit(0)
    elif request.c_method == "DELETE":
        data = category_delete(0)
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
