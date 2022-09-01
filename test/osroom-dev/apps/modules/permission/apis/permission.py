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
from apps.modules.permission.process.permission import permission, permissions, add_per, delete_per, edit_per, \
    permissions_details


@api.route('/admin/permission', methods=['GET', 'POST', 'PUT', 'DELETE'])
@osr_login_required
@permission_required()
def api_permission():
    """
    GET:
        1.获取系统的权限数据详情
        pre:<int>,每页获取几条数据,默认10
        page:<int>,第几页,默认1
        keyword:<str>,搜索关键字
        is_details:<int>, 必须是1

        2.只获取系统的全部权限的value, name, explain, 以及已使用的权重位置
        不填任何参数

    POST:
        添加一个权限
        name:<str>, 名称
    　　 　　 position:<int>, 二进制中的位置
    　　 　　 explain:<str>,说明
        is_default:<int>, 0表示不作为默认权限, 1表示作为默认权限之一
    PUT:
        更新权限
        id:<str>,id
        name:<str>, 名称
    　　 　　 position:<int>, 二进制中的位置
    　　 　　 explain:<str>,说明
        is_default:<int>, 0表示不作为默认权限, 1表示作为默认权限之一

    DELETE:
        删除手动添加的页面路由
        ids:<array>
    :return:
    """

    if request.c_method == "GET":
        if request.argget.all("id"):
            data = permission()
        elif request.argget.all("is_details"):
            data = permissions_details()
        else:
            data = permissions()
    elif request.c_method == "POST":
        data = add_per()
    elif request.c_method == "PUT":
        data = edit_per()
    elif request.c_method == "DELETE":
        data = delete_per()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
