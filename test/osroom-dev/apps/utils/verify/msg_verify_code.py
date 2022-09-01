#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import random
from bson import ObjectId
from flask_babel import gettext
import time
from apps.core.template.get_template import get_email_html
from apps.utils.send_msg.send_email import send_email
from apps.app import mdbs
from apps.core.utils.get_config import get_config
from apps.utils.send_msg.send_message import send_mobile_msg


def _rndChar(i=2):
    """
    随机数字和字母
    :return:
    """
    if i == 1:
        # 字母
        an = random.randint(97, 122)
    else:
        # 数字
        an = random.randint(48, 57)
    return chr(an)


def create_code_send(account, account_type, username=""):
    """
    创建email和message验证码
    :param account:
    :param account_type:
    :return:
    """

    _str = ""
    type = get_config("verify_code", "SEND_CODE_TYPE")
    if type:
        temp_str_list = []
        # 如果存在设置
        if "string" in type and type["string"]:
            for t in range(int(type["string"])):
                c = _rndChar(i=1)
                temp_str_list.append(c)

        if "int" in type and type["int"]:
            for t in range(int(type["int"])):
                c = _rndChar(i=2)
                temp_str_list.append(c)
        # 打乱
        random.shuffle(temp_str_list)
        for c in temp_str_list:
            _str = "{}{}".format(_str, c)

    else:
        for t in range(6):
            i = random.randint(1, 2)
            c = _rndChar(i=i)
            _str = "{}{}".format(_str, c)

    if account_type == "email":

        _code = {
            'str': _str,
            'time': time.time(),
            'to_email': account,
            "type": "msg"
        }
        mdbs["web"].db.verify_code.insert_one(_code)

        subject = gettext("Verification code")
        body = [
            gettext("This is the temporary security code you applied for."),
            gettext("If you didn't operate it, please ignore it.")
        ]
        data = {
            "title": subject,
            "username": username,
            "body": body,
            "code": _str,
            "site_url": get_config("site_config", "SITE_URL")
        }
        html = get_email_html(data, template_path="pages/module/email/send-code.html")

        msg = {
            "subject": subject,
            "recipients": [account],
            "html_msg": html
        }
        send_email(msg=msg, ctype="code")

        return {"msg": gettext("Has been sent. If not, please check spam"),
                "msg_type": "s", "custom_status": 201}

    elif account_type == "mobile_phone":

        _code = {
            'str': _str,
            'time': time.time(),
            'to_tel_number': account,
            "type": "msg"}
        mdbs["web"].db.verify_code.insert_one(_code)
        content = gettext(
            "[{}] Your verification code is: {}. "
            "If you do not send it, please ignore it. "
            "Please do not tell the verification code to others").format(
            get_config(
                "site_config", "APP_NAME"), _str)

        s, r = send_mobile_msg([account], content)
        if not s:
            mdbs["web"].db.verify_code.update_one(
                {
                    "_id": ObjectId(_code['_id'])
                },
                {
                    "$set": {
                        "error": r
                    }
                })
            return {
                "msg": r,
                "msg_type": "w",
                "custom_status": 400
            }

        return {"msg": r, "msg_type": "w", "custom_status": 201}


def verify_code(code, email="", tel_number=""):
    """
    验证email或message验证码
    :param code: 验证码
    :param code:
    :return:
    """
    r = False
    if not code:
        return r
    _code = None
    if email:
        _code = mdbs["web"].db.verify_code.find(
            {
                'to_email': email,
                "type": "msg"
            }).sort([("time", -1)]).limit(1)

    elif tel_number:
        _code = mdbs["web"].db.verify_code.find_one(
            {
                'to_tel_number': tel_number,
                "type": "msg"
            }).sort([("time", -1)]).limit(1)

    if _code and _code.count(True):
        _code = _code[0]
        if _code['str'].lower() == code.lower() and time.time() - \
                _code['time'] < get_config("verify_code", "EXPIRATION"):
            r = True

    return r
