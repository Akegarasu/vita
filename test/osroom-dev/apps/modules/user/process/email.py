#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from flask_babel import gettext
from flask_login import current_user
import time

from apps.modules.user.process.get_or_update_user import update_one_user
from apps.utils.verify.msg_verify_code import verify_code
from apps.modules.user.process.user import insert_op_log
from apps.core.flask.reqparse import arg_verify
from apps.utils.validation.str_format import email_format_ver
from apps.app import mdbs


def email_update():
    """
    更新邮箱绑定
    :return:
    """
    new_email_code = request.argget.all('new_email_code')
    current_email_code = request.argget.all('current_email_code')
    email = request.argget.all('email').strip()
    password = request.argget.all('password').strip()
    s, r = arg_verify(reqargs=[(gettext("email"), email)], required=True)
    data = {}
    if not s:
        data = r
    elif mdbs["user"].db.user.find_one({"_id": {"$ne": current_user.id}, "email": email}):
        data = {'msg': gettext("This E-mail address has been registered"),
                'msg_type': "w", "custom_status": 403}

    elif mdbs["user"].db.user.find_one({"_id": current_user.id, "email": email}):
        data = {'msg': gettext("This is the email address you currently use"),
                'msg_type': "w", "custom_status": 403}
    if data:
        return data

    r, msg = email_format_ver(email)
    if not r:
        return {"msg": msg, "msg_type": "w", "custom_status": 422}
    elif not current_email_code and current_user.email:
        data = {
            "msg": gettext("Invalid verification code [currently bound]"),
            "msg_type": "w",
            "custom_status": 401}
        return data
    elif not new_email_code:
        data = {
            "msg": gettext("Invalid verification code [ready to bind]"),
            "msg_type": "w",
            "custom_status": 401}
        return data

    data = p_email_change(new_email_code, current_email_code, email, password)
    return data


def p_email_change(new_email_code, current_email_code, email, password):
    """
    用户邮箱修改
    :param code_group:(code_id, code)
    :param current_code_group:(current_email_code_id, current_email_code)
    :param email:
    :param password:
    :return:
    """
    # 验证当前邮箱收到的验证码，保证用户自己修改的
    if current_user.email:
        r = verify_code(current_email_code, current_user.email)
        if not r:
            oplog = {
                'op_type': 'set_email',
                'time': time.time(),
                'status': 'f',
                'info': 'Verification code mistake[currently bound]',
                'ip': request.remote_addr
            }

            insert_op_log(oplog)
            data = {
                "msg": gettext("Verification code error [currently bound]"),
                "msg_type": "w",
                "custom_status": 401}
            return data

    # 验证新邮箱收到的验证码，保证绑定的邮箱无误
    r = verify_code(new_email_code, email)
    if not r:
        oplog = {
            'op_type': 'set_email',
            'time': time.time(),
            'status': 'f',
            'info': 'Verification code mistake[ready to bind]',
            'ip': request.remote_addr
        }

        insert_op_log(oplog)
        data = {
            "msg": gettext("Verification code error [ready to bind]"),
            "msg_type": "w",
            "custom_status": 401}
        return data

    if current_user.verify_password(password) or not current_user.email:
        update_one_user(
            user_id=current_user.str_id,
            updata={
                "$set": {
                    "email": email}})
        oplog = {
            'op_type': 'set_email',
            'time': time.time(),
            'status': 's',
            'info': '',
            'ip': request.remote_addr
        }

        insert_op_log(oplog)
        data = {
            "msg": gettext("Email is changed"),
            "msg_type": "s",
            "custom_status": 201}
    else:
        oplog = {
            'op_type': 'set_email',
            'time': time.time(),
            'status': 'f',
            'info': 'Password mistake',
            'ip': request.remote_addr
        }
        insert_op_log(oplog)
        data = {
            'msg': gettext('Password mistake'),
            'msg_type': 'e',
            "custom_status": 401}

    return data
