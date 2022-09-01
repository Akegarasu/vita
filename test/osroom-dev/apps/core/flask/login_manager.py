#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from functools import wraps
from flask import request, current_app
from flask_babel import gettext
from flask_login import current_user
from flask_login.config import EXEMPT_METHODS
from werkzeug.exceptions import Unauthorized



def osr_login_required(func):
    """
    If you decorate a view with this, it will ensure that the current user is
    logged in and authenticated before calling the actual view. (If they are
    not, it calls the :attr:`LoginManager.unauthorized` callback.) For
    example::

        @app.route('/post')
        @osr_login_required
        def post():
            pass

    If there are only certain times you need to require that your user is
    logged in, you can do so with::

        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

    ...which is essentially the code that this function adds to your views.

    It can be convenient to globally turn off authentication when unit testing.
    To enable this, if the application configuration variable `LOGIN_DISABLED`
    is set to `True`, this decorator will be ignored.

    .. Note ::

        Per `W3 guidelines for CORS preflight requests
        <http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0>`_,
        HTTP ``OPTIONS`` requests are exempt from login checks.

    :param func: The view function to decorate.
    :type func: function
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:

            response = current_app.make_response(
                gettext("Anonymous users can not access '{}', need to log in").format(
                    request.path))
            raise LoginReqError(
                response.get_data(
                    as_text=True),
                response=response)

        return func(*args, **kwargs)
    return decorated_view


class LoginReqError(Unauthorized):
    """
    错误请求类： 未登录
    """
    description = gettext('Anonymous users can not access, you need to log in')
