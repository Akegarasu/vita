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
from apps.modules.follow.process.user_follow import get_followed_users, get_fans_users, follow_user, unfollow


@api.route('/user/follow', methods=['GET'])
@permission_required(use_default=False)
def api_get_user_follow():
    """
    GET:
        获取用户关注的用户
        user_id:<str>, 用户ID
        action:<str>,　为followed_user

        获取当前的登录用户的粉丝
        action:<str>,　为fans

    :return:
    """

    if request.c_method == "GET":
        if request.argget.all("action") == "followed_user":
            data = get_followed_users()
        else:
            data = get_fans_users()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)


@api.route('/user/follow', methods=["POST", 'DELETE'])
@osr_login_required
@permission_required(use_default=False)
def api_user_follow():
    """

    POST:
        当前登录用户关注另一个用户用户
        ids:<array>,需关注用户的user id

    DELETE:
        当前登录用户取消关注一个用户
        ids:<array>,不再关注的用户的user id
    :return:
    """

    if request.c_method == "POST":
        data = follow_user()

    elif request.c_method == "DELETE":
        data = unfollow()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
