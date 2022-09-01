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
from apps.modules.user.process.adm_user import user, users, user_restore, user_activation, user_edit, user_del, add_user


@api.route('/admin/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
@osr_login_required
@permission_required()
def api_adm_user():
    """
    GET:
        1. 获取指定ID的用户基本信息
        id:<str> , user id

        2.分页获取所有用户
        status:<str>,用户状态，"normal"　or "inactive" or "cancelled"
        page:<int>,第几页，默认第1页
        pre:<int>, 每页查询多少条
        keyword:<str>, Search keywords, 搜索的时候使用
    POST:
        添加用户
        email：<email>, 非必须
        mobile_phone_number：<num>, 非必须
        username:<str>
        password:<str>
        password2:<str>

    PUT:
        1.编辑用户
        id:<str>, user id
        role_id:<str>, role id
        active:<int>, 0 or 1

        2.激活或冻结用户
        op:<str>, 为"activation"
        active:<int>, 0 or 1, 0为冻结, 1为激活
        ids:<array>

        3.恢复用户,将状态改为未删除
        op:<str>, 为"restore"
        ids:<array>

    DELETE:
        删除用户,非数据库删除
        ids:<array>
    """
    if request.c_method == "GET":
        if request.argget.all('id'):
            data = user()
        else:
            data = users()
    elif request.c_method == "POST":
        data = add_user()
    elif request.c_method == "PUT":
        if request.argget.all('op') == "restore":
            data = user_restore()
        elif request.argget.all('op') == "activation":
            data = user_activation()
        else:
            data = user_edit()

    elif request.c_method == "DELETE":
        data = user_del()

    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)


@api.route('/admin/user/del', methods=['DELETE'])
@osr_login_required
@permission_required()
def api_adm_user_del():
    """

    DELETE:
        永久删除用户,数据库中删除
        ids:<array>
        permanent:<int> 0 or 1, 0:非数据库删除,只是把状态改成"删除状态",为1:表示永久删除,

    """

    if request.c_method == "DELETE":
        data = user_del()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
