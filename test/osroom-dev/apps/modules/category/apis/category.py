#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from flask_babel import gettext

from apps.core.flask.login_manager import osr_login_required

from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.reqparse import arg_verify
from apps.core.flask.response import response_format
from apps.modules.category.process.category import categorys, category_add, category_edit, \
    category_delete, get_category_type, get_category_info


@api.route('/content/category/info', methods=['GET'])
@permission_required(use_default=False)
def api_category_info():
    """
    获取指定category id的category信息
    :return:
    """

    data = get_category_info()
    return response_format(data)


@api.route('/content/user/post/category', methods=['GET'])
@permission_required(use_default=False)
def api_get_user_category():
    """
    GET:

    action: < str >, 'get_category'
    type: < str >, 'post'
    user_id:<str>
    """
    if request.c_method == "GET":
        user_id = request.argget.all('user_id')
        s, r = arg_verify([(gettext("user_id"), user_id)], required=True)
        if not s:
            data = r
        else:
            data = categorys(user_id=user_id)
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)


@api.route('/content/category', methods=['GET', 'POST', 'PUT', 'DELETE'])
@osr_login_required
@permission_required(use_default=False)
def api_category():
    """
    GET:

        action:<str>, 可以为get_category, get_category_type, 默认get_category
        1.获取当前用户指定的type的所有category
            action:<str>, 为get_category
            type:<str>, 你设置的那几个类别中的类别,在config.py文件中category, 可在网站管理端设置的

        2. 获取所有的type: config.py文件中category的所有CATEGORY TYPE
            action:<str>, 为get_category_type
        解释:
            在分类中(category)又分为几种类型(type)
            如: type为post有几个category

    POST:
        添加文集
        name:<str>
        type:<str>, 只能是你设置的那几个类别,在config.py文件中category, 或者网站管理设置
    PUT:
        修改文集
        id:<str>, post category id
        name:<str>
    DELETE:
        删除文集名称
        ids:<array>, post category ids
    """
    if request.c_method == "GET":
        if not request.argget.all("action") == "get_category_type":
            data = categorys()
        else:
            data = get_category_type()

    elif request.c_method == "POST":
        data = category_add()
    elif request.c_method == "PUT":
        data = category_edit()
    elif request.c_method == "DELETE":
        data = category_delete()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
