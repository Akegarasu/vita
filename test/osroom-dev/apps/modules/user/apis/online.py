#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from flask_babel import gettext
from flask_login import logout_user
from apps.configs.sys_config import LOGIN_PLATFORM
from apps.core.auth.jwt_auth import JwtAuth
from apps.core.blueprint import api, open_api
from apps.core.flask.reqparse import arg_verify
from apps.core.flask.response import response_format
from apps.modules.user.process.online import sign_up, sign_in
from apps.core.utils.get_config import get_config
from apps.modules.user.process.sign_in import third_party_sign_in
from apps.utils.format.obj_format import str_to_num


@api.route('/sign-up', methods=['POST'])
def api_sign_up():
    """
    POST:
        1.普通用户使用邮箱注册a
        emial:<emial>, 邮箱
        username: <str>, 用户名
        password: <str>,密码
        password2: <str>,再次确认密码
        code:<str>, 邮箱收取到的code


        2.普通用户使用手机注册a
        mobile_phone_number:<int>手机号码
        username: <str>, 用户名
        password: <str>,密码
        password2: <str>,再次确认密码
        code:<str>, 手机收取到的code

        :return:
    """
    data = sign_up()
    return response_format(data)


@api.route('/sign-in', methods=['PUT'])
def api_sign_in():
    """
    PUT:
        1.普通登录
        username: <str>, 用户名或邮箱或手机号码
        password: <str>,密码
        remember_me:<bool>,是否保存密码
        next:<str>, 登录后要返回的to url, 如果为空,则返回设置中的LOGIN_TO
        use_jwt_auth:<int>, 是否使用jwt验证. 0 或 1,默认为0不使用

        当多次输入错误密码时，api会返回open_img_verif_code:true,
        表示需要图片验证码验证,客户端应该请求验证码/api/vercode/image,
         然后后再次提交登录时带下如下参数
        再次提交登录时需要以下两个参数
        code:<str>, 图片验证码中的字符
        code_url_obj:<json>,图片验证码url 对象
        :return:

        2.第三方登录
        待开发插件入口
    """

    data = sign_in()
    return response_format(data)


@open_api.route(
    '/sign-in/third-party/<platform>/callback',
    methods=[
        'GET',
        'PUT',
        'POST'])
def api_sign_in_third_party(platform):
    """
    PUT & POST & GET:
        第三方平台授权登录回调
        platform: 平台名称：可以是wechat, qq, github, sina_weibo, alipay, facebook, twitter等
                可在sys_config.py文件中配置LOGIN_PLATFORM
        :return:
    """

    s, r = arg_verify(reqargs=[("platform", platform)],
                      only=LOGIN_PLATFORM)
    if not s:
        data = r
    else:
        data = third_party_sign_in(platform)
    return response_format(data)


@api.route('/sign-out', methods=['GET', 'PUT'])
def sign_out():
    """
    GET or PUT:
        用户登出api
        use_jwt_auth:<int>, 是否使用jwt验证. 0 或 1,默认为0不使用.
                     如果是jwt验证登录信息的客户端use_jwt_auth应为1
        :param adm:
        :return:
    """

    use_jwt_auth = str_to_num(request.argget.all('use_jwt_auth', 0))
    if use_jwt_auth:

        # 使用jwt验证的客户端登出
        jwt_auth = JwtAuth()
        s, r = jwt_auth.clean_login()
        if s:
            data = {
                "msg": gettext("Successfully logged out"),
                "msg_type": "s",
                "custom_status": 201,
                "to_url": get_config(
                    "login_manager",
                    "LOGIN_OUT_TO")}
        else:
            data = {"msg": r, "msg_type": "s", "custom_status": 400}
    else:
        logout_user()

        data = {
            "msg": gettext("Successfully logged out"),
            "msg_type": "s",
            "custom_status": 201,
            "to_url": get_config(
                "login_manager",
                "LOGIN_OUT_TO")}
    return response_format(data)
