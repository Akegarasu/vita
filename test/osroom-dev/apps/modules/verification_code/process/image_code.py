#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.utils.verify.img_verify_code import create_img_code


def get_code():
    """
    获取图片验证码
    :return:
    """
    data = {"msg_type": "s", "custom_status": 200}
    code = create_img_code()
    data['code'] = code
    return data
