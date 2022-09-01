#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.login_manager import osr_login_required
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.permission.process.url_permission import get_urls, get_url, update_url, add_url, delete_url


@api.route('/admin/url/permission', methods=['GET', 'POST', 'PUT', 'DELETE'])
@osr_login_required
@permission_required()
def api_url_permission():
    """
    GET:
        获取系统的web url
        type:<array>,类型, 可选api, static, page
        pre:<int>,每页获取几条数据,默认10
        page:<int>,第几页,默认1
        keyword:<str>,搜索关键字
    POST:
        添加页面路由
        url:<str>, 只用于添加页面路由
    PUT:
        更新权限
        id:<str>,id
        method:<str>
        custom_permission:<array>, 如[1, 512, 128]
        login_auth:<int>, 0 或　１, 是否需要登录验证(如果原代码路由中未指定需要登录请求, 则按照此配置)

    DELETE:
        删除手动添加的页面路由
        ids:<array>
    :return:
    """

    if request.c_method == "GET":
        if request.argget.all("id"):
            data = get_url()
        else:
            data = get_urls()
    elif request.c_method == "POST":
        data = add_url()
    elif request.c_method == "PUT":
        data = update_url()
    elif request.c_method == "DELETE":
        data = delete_url()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
