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
from apps.modules.user.process.role import role, roles, add_role, edit_role, delete_role



@api.route('/admin/role', methods=['GET', 'POST', 'PUT', 'DELETE'])
@osr_login_required
@permission_required()
def api_role():
    """
    GET:
        1. 获取指定ID的角色
        id:<str> ,role id

        2.分页获取全部角色
        page:<int>,第几页，默认第1页
        pre:<int>, 每页查询多少条
    POST:
        添加一个角色
        name:<str>
        instructions:<str>
        default:<int or bool>, 0 or 1
        permissions:<array>, 数组，可以给角色指定多个权重, 如[1, 2, 4, 128]

    PUT:
        修改一个角色
        id:<str>, role id
        name:<str>
        instructions:<str>
        default:<int>, 0 or 1
        permissions:<array>, 数组，可以给角色指定多个权重, 如[1, 2, 4, 128]

    DELETE:
        删除角色
        ids:<arry>, role ids
    """

    if request.c_method == "GET":
        if request.argget.all('id'):
            data = role()
        else:
            data = roles()

    elif request.c_method == "POST":
        data = add_role()

    elif request.c_method == "PUT":
        data = edit_role()

    elif request.c_method == "DELETE":
        data = delete_role()

    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
