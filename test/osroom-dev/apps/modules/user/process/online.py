#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask_babel import gettext
from apps.utils.format.obj_format import json_to_pyseq, str_to_num
from apps.core.utils.get_config import get_config
from apps.modules.user.process.sign_in import p_sign_in
from flask import request
from apps.modules.user.process.sign_up import p_sign_up


def sign_up():

    if not get_config("login_manager", "OPEN_REGISTER"):
        data = {
            "msg": gettext('Sorry, temporarily unregistered function'),
            "msy_type": "w",
            "custom_status": 401}
    else:
        email = request.argget.all('email', '').strip()
        mobile_phone_number = str_to_num(
            request.argget.all(
                'mobile_phone_number', 0))
        username = request.argget.all('username', '').strip()
        password = request.argget.all('password', '').strip()
        password2 = request.argget.all('password2', '').strip()
        code = request.argget.all('code', '').strip()

        data = p_sign_up(email=email, mobile_phone_number=mobile_phone_number,
                         username=username, password=password,
                         password2=password2, code=code)
    return data


def sign_in():

    username = request.argget.all('username', '').strip()
    password = request.argget.all('password', '').strip()
    code = request.argget.all('code', '').strip()
    code_url_obj = json_to_pyseq(request.argget.all('code_url_obj', {}))
    remember_me = request.argget.all('remember_me', 0)
    use_jwt_auth = str_to_num(request.argget.all('use_jwt_auth', 0))
    try:
        remember_me = int(remember_me)
    except BaseException:
        data = {
            "d_msg": gettext("remember_me requires an integer"),
            "d_msg_type": "e",
            "custom_status": 400}
        return data

    data = p_sign_in(
        username=username,
        password=password,
        code_url_obj=code_url_obj,
        code=code,
        remember_me=remember_me,
        use_jwt_auth=use_jwt_auth)

    return data
