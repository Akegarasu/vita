#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.core.template.get_template import get_email_html
from apps.core.utils.get_config import get_config
from apps.modules.user.process.get_or_update_user import insert_one_user
from apps.utils.send_msg.send_email import send_email
from apps.utils.send_msg.send_message import send_mobile_msg
from apps.utils.validation.str_format import email_format_ver, password_format_ver, short_str_verifi, mobile_phone_format_ver
from apps.app import mdbs
from apps.modules.user.models.user import user_model
from apps.utils.verify.msg_verify_code import verify_code


def p_sign_up(
        username,
        password,
        password2,
        code,
        email=None,
        mobile_phone_number=None):
    """
    普通用户注册函数
    :return:
    """
    data = {}
    if current_user.is_authenticated:
        data['msg'] = gettext("Is logged in")
        data["msg_type"] = "s"
        data["custom_status"] = 201
        data['to_url'] = request.argget.all(
            'next') or get_config("login_manager", "LOGIN_IN_TO")
        return data

    # 用户名格式验证
    s1, r1 = short_str_verifi(username, project="username")
    # 密码格式验证
    s2, r2 = password_format_ver(password)
    if not s1:
        data = {'msg': r1, 'msg_type': "e", "custom_status": 422}
    elif mdbs["user"].db.user.find_one({"username": username}):
        # 是否存在用户名
        data = {
            'msg': gettext("Name has been used"),
            'msg_type': "w",
            "custom_status": 403}
    elif not s2:
        data = {'msg': r2, 'msg_type': "e", "custom_status": 400}
        return data
    elif password2 != password:
        # 检验两次密码
        data = {
            'msg': gettext("The two passwords don't match"),
            'msg_type': "e",
            "custom_status": 400}
    if data:
        return data

    if email:
        # 邮件注册
        # 邮箱格式验证
        s, r = email_format_ver(email)
        if not s:
            data = {'msg': r, 'msg_type': "e", "custom_status": 422}
        elif mdbs["user"].db.user.find_one({"email": email}):
            # 邮箱是否注册过
            data = {
                'msg': gettext("This email has been registered in the site oh, please login directly."),
                'msg_type': "w",
                "custom_status": 403}
        if data:
            return data

        # 检验验证码
        r = verify_code(code=code, email=email)
        if not r:
            data = {
                'msg': gettext("Verification code error"),
                'msg_type': "e",
                "custom_status": 401}
            return data

    elif mobile_phone_number:
        # 手机注册
        s, r = mobile_phone_format_ver(mobile_phone_number)
        if not s:
            data = {'msg': r, 'msg_type': "e", "custom_status": 422}
        elif mdbs["user"].db.user.find_one({"mphone_num": mobile_phone_number}):
            # 手机是否注册过
            data = {
                'msg': gettext("This number has been registered in the site oh, please login directly."),
                'msg_type': "w",
                "custom_status": 403}

        if data:
            return data

        # 检验验证码
        r = verify_code(code=code, tel_number=True)
        if not r:
            data = {
                'msg': gettext("Verification code error"),
                'msg_type': "e",
                "custom_status": 401}
            return data

    if not data:
        # 用户基本信息
        role_id = mdbs["user"].db.role.find_one(
            {"default": {"$in": [True, 1]}})["_id"]
        user = user_model(username=username,
                          email=email,
                          mphone_num=mobile_phone_number,
                          password=password,
                          custom_domain=-1,
                          role_id=str(role_id),
                          active=True)
        r = insert_one_user(updata=user)
        if r.inserted_id:
            if email:
                # 发送邮件
                subject = gettext("Registration success notification")
                body = [
                    gettext("Welcome to register {}.").format(get_config("site_config", "APP_NAME")),
                    gettext("{} registered the account successfully.").format(email)
                ]
                data = {
                    "title": subject,
                    "username": username,
                    "body": body,
                    "site_url": get_config("site_config", "SITE_URL")
                }
                html = get_email_html(data)

                msg = {
                    "subject": subject,
                    "recipients": [email],
                    "html_msg": html
                }
                send_email(msg=msg, ctype="nt")

            elif mobile_phone_number:
                # 发送短信
                content = gettext("[{}] Successful registration account.").format(
                    get_config("site_config", "APP_NAME")
                )
                send_mobile_msg(mobile_phone_number, content)

            data = {'msg': gettext('Registered successfully'),
                    'to_url': '/sign-in',
                    'msg_type': 's', "custom_status": 201}
        else:
            data = {'msg': gettext('Data saved incorrectly, please try again'),
                    'msg_type': 'e', "custom_status": 201}
        return data

    return data
