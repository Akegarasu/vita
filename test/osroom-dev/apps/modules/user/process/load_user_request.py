#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.app import login_manager
from apps.core.auth.jwt_auth import JwtAuth
from apps.modules.user.process.user import User, AnonymousUser
# JWT验证
jwt_auth = JwtAuth()


@login_manager.user_loader
def load_user(user_id):
    """
    当检测到用户已登录时回调此函数(登录针对非BearerToken验证用户的客户端,如普通浏览器)
    :param user_id:
    :return:用户实例
    """
    user = User(user_id)
    return user


@login_manager.request_loader
def load_user_req(request):
    """
    当检测到用户未登录时回调此函数(未登录针对的是cookie session的客户端,如普通浏览器)
    如果客户端使用的是api携带登录token, 则进行验证后返回对应用户信息
    :param request:
    :return:
    """
    s, user = jwt_auth.user_identify()
    if s:
        # 鉴权成功, 返回用户实例
        return user
    else:
        # 鉴权失败
        amuser = AnonymousUser()
        return amuser
