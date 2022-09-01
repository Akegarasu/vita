#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from flask_babel import gettext
from apps.core.auth.rest_token_auth import RestTokenAuth
from apps.core.flask.reqparse import arg_verify
rest_token_auth = RestTokenAuth()


def get_secret_token():
    """
    获取jwt access token
    :return:
    """
    data = {"msg_type": "s"}
    data["secret_token"] = rest_token_auth.get_secret_tokens["token_info"]
    return data


def create_secret_token():
    """
    创建一个新的jwt access token
    :return:
    """

    data = {
        "msg_type": "s",
        "msg": gettext("Created successfully"),
        "custom_status": 201}
    s, r = rest_token_auth.create_secret_token()
    if not s:
        data = {"msg_type": "w", "msg": r, "custom_status": 403}

    return data


def activate_secret_token():
    """
    激活新的access token
    :return:
    """

    token_id = request.argget.all("token_id")
    s, r = arg_verify([("token id", token_id)], required=True)
    if not s:
        return r
    s, r = rest_token_auth.activate_secret_token(token_id)
    if s:
        data = {"msg_type": "s", "msg": r, "custom_status": 201}
    else:
        data = {"msg_type": "w", "msg": r, "custom_status": 400}
    return data


def disable_secret_token():
    """
    禁用access token
    :return:
    """

    token_id = request.argget.all("token_id")
    s, r = arg_verify([("token id", token_id)], required=True)
    if not s:
        return r

    s, r = rest_token_auth.disable_secret_token(token_id)
    if s:
        data = {"msg_type": "s", "msg": r, "custom_status": 201}
    else:
        data = {"msg_type": "w", "msg": r, "custom_status": 400}
    return data


def delete_secret_token():
    """
    删除access token
    :return:
    """

    token_id = request.argget.all("token_id")
    s, r = arg_verify([("token id", token_id)], required=True)
    if not s:
        return r
    s, r = rest_token_auth.delete_secret_token(token_id)
    if s:
        data = {"msg_type": "s", "msg": r, "custom_status": 201}
    else:
        data = {"msg_type": "w", "msg": r, "custom_status": 400}
    return data
