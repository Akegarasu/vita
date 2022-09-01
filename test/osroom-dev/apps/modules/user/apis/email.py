#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.core.flask.login_manager import osr_login_required
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.user.process.email import email_update


@api.route('/account/email', methods=['PUT'])
@osr_login_required
@permission_required(use_default=False)
def api_account_email():
    """
    PUT
        账户邮件修改
        email:<email>, 要绑定的新邮箱
        new_email_code:<str>, 新邮箱收取到的验证码,用于保证绑定的邮箱时用户自己的
        current_email_code:<str>, 当前邮箱收取的验证码,用于保证邮箱修改是用户自己发起
        password:<str>, 账户的登录密码

        :return:
    """
    data = email_update()
    return response_format(data)
