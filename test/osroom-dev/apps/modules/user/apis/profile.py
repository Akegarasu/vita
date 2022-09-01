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
from apps.modules.user.process.profile import profile_update, public_profile, user_basic_edit, all_profile


@api.route('/account/profile/public', methods=['GET'])
@permission_required(use_default=False)
def user_public():
    """
    GET:
        获取用户公开信息
        user_id:<str>
        is_basic:<int>, 0或1,默认1. 为１时只获取最基本的用户信息
        :return:
    """
    data = public_profile()
    return response_format(data)


@api.route('/account/basic', methods=['PUT'])
@osr_login_required
@permission_required(use_default=False)
def api_account_basic():
    """
    用户基础设置
    PUT:
        编辑用户基础设置
        username:<str>, 新的用户名
        custom_domain:<str>, 个性域名
        editor:<str>, 'rich_text' or 'markdown' 如果你有多个文本编辑器的话，可以加入这个选项
    :return:
    """

    data = user_basic_edit()
    return response_format(data)


@api.route('/account/profile', methods=['GET', 'PUT'])
@osr_login_required
@permission_required(use_default=False)
def api_account_profile():
    """
    用户资料
    GET:
        获取当前登录用户的信息
        is_basic:<int>, 0或1,默认1. 为１时只获取最基本的用户信息
    PUT
        更新用户资料
        gender:<str>, m or f or secret
        birthday:<int or str>, The format must be "YYYYMMDD" ,such as: 20170101
        address:<dict>, The format must be: {countries:'string', provinces:'string',
                                             city:'string', district:'string', detailed:'string'}
        info:<str>

    :return:
    """

    if request.c_method == "GET":

        data = all_profile()
    elif request.c_method == "PUT":
        data = profile_update()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
