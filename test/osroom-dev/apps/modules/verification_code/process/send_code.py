#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import time
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.app import mdbs
from apps.core.flask.reqparse import arg_verify
from apps.core.utils.get_config import get_config
from apps.modules.user.process.get_or_update_user import get_one_user
from apps.utils.format.obj_format import json_to_pyseq, str_to_num
from apps.utils.validation.str_format import email_format_ver, mobile_phone_format_ver
from apps.utils.verify.img_verify_code import create_img_code, verify_image_code
from apps.utils.verify.msg_verify_code import create_code_send


def send_code():
    """
    发送验证码
    :return:
    """
    data = {}
    account_type = request.argget.all('account_type', "email").strip()
    account = request.argget.all('account')
    exist_account = str_to_num(request.argget.all('exist_account', 0))
    code = request.argget.all('code', '').strip()
    code_url_obj = json_to_pyseq(request.argget.all('code_url_obj', {}))

    s, r = arg_verify(reqargs=[("account_type", account_type)],
                      only=["email", "mobile_phone"])
    if not s:
        return r
    username = ""
    if account_type == "email":
        s, r = arg_verify(reqargs=[(gettext("Email"), account)], required=True)
        if not s:
            return r
        # 邮箱格式验证
        r, s = email_format_ver(account)
        if not r:
            data = {'msg': s, 'msg_type': "e", "custom_status": 422}
            return data

        if exist_account:
            temp_user = get_one_user(email=account)
            if not temp_user:
                data = {
                    'msg': gettext("This account is not registered on this platform"),
                    'msg_type': "w",
                    "custom_status": 400}
                return data
            username = temp_user["username"]
        r, s = call_verification(code_url_obj, code)
        if not r:
            return s

        data = create_code_send(
            account=account,
            account_type=account_type,
            username=username
        )

    elif account_type == "mobile_phone":
        s, r = arg_verify(
            reqargs=[
                (gettext("Telephone number"), account)], required=True)
        if not s:
            return r

        # 移动号码格式格式验证
        r, s = mobile_phone_format_ver(account)
        if not r:
            data = {'msg': s, 'msg_type': "e", "custom_status": 422}
            return data

        if exist_account:
            user_query = {"mphone_num": account}
            temp_user = get_one_user(mphone_num=account)
            if not temp_user:
                data = {
                    'msg': gettext("This account is not registered on this platform"),
                    'msg_type': "w",
                    "custom_status": 400}
                return data
            username = temp_user["username"]

        r, s = call_verification(code_url_obj, code)
        if not r:
            return s
        data = create_code_send(account=account, account_type=account_type, username=username)

    return data


def call_verification(code_url_obj, code):
    """
    记录调用次数,并查看是否有调用权限
    :return:
    """

    # 记录调用
    if current_user.is_authenticated:
        user_id = current_user.str_id
    else:
        user_id = None
    mdbs["sys"].db.sys_call_record.insert_one({"type": "api",
                                           "req_path": request.path,
                                           "ip": request.remote_addr,
                                           "user_id": user_id,
                                           "time": time.time()})
    # 查找1分钟内本IP的调用次数
    freq = mdbs["sys"].db.sys_call_record.find(
        {
            "type": "api",
            "req_path": request.path,
            "ip": request.remote_addr,
            "user_id": user_id,
            "time": {
                "$gte": time.time() -
                60}}).count(True)

    if freq:
        if freq > get_config("verify_code", "MAX_NUM_SEND_SAMEIP_PERMIN"):
            # 大于单位时间最大调用次数访问验证
            data = {
                'msg': gettext(
                    "The system detects that your network is sending verification codes frequently."
                    " Please try again later!"),
                'msg_type': "w",
                "custom_status": 401}
            return False, data

        elif freq > get_config("verify_code", "MAX_NUM_SEND_SAMEIP_PERMIN_NO_IMGCODE") + 1:
            # 已超过单位时间无图片验证码情况下的最大调用次数, 验证图片验证码
            # 检验图片验证码
            r = verify_image_code(code_url_obj, code)
            if not r:
                data = {
                    'msg': gettext("Image verification code error, email not sent"),
                    'msg_type': "e",
                    "custom_status": 401}
                # 验证错误,开启验证码验证
                data["open_img_verif_code"] = True
                data["code"] = create_img_code()
                return False, data

        elif freq > get_config("verify_code", "MAX_NUM_SEND_SAMEIP_PERMIN_NO_IMGCODE"):
            # 如果刚大于单位时间内，无图片验证码情况下的最大调用次数, 返回图片验证码验证码
            data = {
                'msg': gettext(
                    "The system detected that your operation is too frequent and"
                    " you need to verify the picture verification code"),
                'msg_type': "w",
                "custom_status": 401}

            data["open_img_verif_code"] = True
            data["code"] = create_img_code()
            return False, data

    return True, ""
