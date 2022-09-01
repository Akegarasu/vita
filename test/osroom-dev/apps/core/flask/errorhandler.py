#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os
from flask import request, render_template, g
from flask_babel import gettext
from flask_wtf.csrf import CSRFError
from werkzeug.utils import redirect

from apps.configs.sys_config import DEFAULT_ADMIN_LOGIN_PAGE
from apps.core.auth.rest_token_auth import OsrTokenError, SecretTokenError, AccessTokenError
from apps.core.blueprint import api, theme_view, admin_view
from apps.core.flask.login_manager import LoginReqError
from apps.core.flask.response import response_format
from apps.core.template.template import render_absolute_path_template
from apps.core.utils.get_config import get_config
from apps.modules.global_data.process.global_data import get_global_site_data


class ErrorHandler:

    """
    配置各种异常状态返回数据 http status
    """

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):

        @app.errorhandler(401)
        def internal_server_error_401(e):
            return internal_server_error(e)

        @app.errorhandler(404)
        def internal_server_error_404(e):
            return internal_server_error(e)

        @app.errorhandler(500)
        def internal_server_error_500(e):
            return internal_server_error(e)

        @app.errorhandler(SecretTokenError)
        def handle_rest_token_error(e):
            data = {
                "custom_status": e.code,
                "msg": e.description,
                "msg_type": "e",
                "error_id": 40101}
            return response_format(data)

        @app.errorhandler(AccessTokenError)
        def handle_rest_token_error(e):
            data = {
                "custom_status": e.code,
                "msg": e.description,
                "msg_type": "e",
                "error_id": 40102}
            return response_format(data)

        @app.errorhandler(CSRFError)
        def handle_csrf_error(e):
            data = {
                "custom_status": e.code,
                "msg": e.description,
                "msg_type": "e",
                "error_id": 40103}
            return response_format(data)

        @app.errorhandler(OsrTokenError)
        def handle_osr_token_error(e):
            data = {
                "custom_status": e.code,
                "msg": e.description,
                "msg_type": "e",
                "error_id": 40104,
                "help": gettext(
                    "Please add the 'OSR-RestToken' or 'X-CSRFToken' request header,"
                    " the specific use please refer to the osroom system documentation:"
                    " http://osroom.com")}
            return response_format(data)

        @app.errorhandler(LoginReqError)
        def handle_login_error(e):
            data = {
                "custom_status": e.code,
                "msg": gettext("Not logged in"),
                "error_msg": e.description,
                "msg_type": "e",
                "to_url": get_config(
                    "login_manager",
                    "LOGIN_VIEW"),
                "error_id": 40105}
            if request.headers.get('OSR-RestToken'):
                data["to_url"] = get_config("login_manager", "LOGIN_VIEW")

            if request.path.startswith(api.url_prefix):
                # api 响应Json数据
                return response_format(data)
            # 页面, 跳转到登录
            if request.path.startswith("/osr-admin"):
                return redirect(DEFAULT_ADMIN_LOGIN_PAGE)
            else:
                return redirect(data["to_url"])


def internal_server_error(e):
    """
    处理服务器错误
    :param e:
    :return:
    """
    try:
        code = e.code
    except BaseException:
        code = 500
    msg_type = "w"
    msg = gettext("An error occurred. Please contact the administrator")
    if code == 401:
        msg = gettext("Permission denied")

    elif code == 404:
        msg = gettext("The api does not exist or has been deprecated")

    elif code == 500:
        msg = gettext("Server error")
        msg_type = "e"

    elif isinstance(code, int) and code // 500 == 1:
        msg = gettext(
            "Server error, please check whether the third-party plug-in is normal")
        msg_type = "e"

    data = {
            "http_status": code,
            "custom_status": None,
            "request_id": g.weblog_id,
            "msg": msg,
            "msg_type": msg_type}

    if request.path.startswith(api.url_prefix):
        return response_format(data)
    else:
        g.site_global = dict(g.site_global,
                             **get_global_site_data(req_type="view"))
        path = "{}/pages/{}.html".format(
            # get_config("theme", "CURRENT_THEME_NAME"),
            g.get_config("theme", "CURRENT_THEME_NAME"),
            code
        )
        absolute_path = os.path.abspath(
            "{}/{}".format(theme_view.template_folder, path))
        if not os.path.isfile(absolute_path):
            # 主题不存在<e.code>错误页面(如404页面),使用系统自带的页面
            path = "{}/module/exception/{}.html".format(
                admin_view.template_folder, code)
            return render_absolute_path_template(path, data=data), 404

        return render_template(path, data=data), code
