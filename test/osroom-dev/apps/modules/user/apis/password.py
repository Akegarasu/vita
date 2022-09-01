#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.core.flask.login_manager import osr_login_required
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.user.process.password import account_password_reset, account_password_retrieve


@api.route('/account/password/reset', methods=['PUT'])
@osr_login_required
@permission_required(use_default=False)
def api_account_password_reset():
    """
    PUT:
        账户密码重设
        now_password:<str>,目前使用的密码
        password:<str>, 新密码
        password2:<str>, 再次确认新密码
        :return:
    """
    data = account_password_reset()
    return response_format(data)


@api.route('/account/password/retrieve', methods=['PUT', 'POST'])
@permission_required(use_default=False)
def api_account_password_retrieve():
    """
    PUT:
        忘记密码,重设
        获取验证码,只需要传回参数email,return回一个{code:{'_id':'', str:'',time:'' }}
        设置新密码,需要全部参数
        email_code:<str>, 邮件中收到的验证码
        email:<str>, 邮箱
        password:<str>, 新密码
        password2:<str>, 再次确认密码
        :return:
    """
    data = account_password_retrieve()
    return response_format(data)
