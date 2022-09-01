#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from flask import request
from apps.configs.sys_config import METHOD_WARNING
from apps.modules.search.process.search import clear_search_logs, \
    get_search_logs, search_process


@api.route('/search', methods=['GET'])
@permission_required(use_default=False)
def api_search():
    """
    GET:
        搜索(暂不支持全文搜索), 只能搜索文章, 用户
        keyword:<str>, Search keywords
        target:<str>, 可选"post" 或 "user". 不使用此参数则搜索所有可选目标
        page:<int>,第几页，默认第1页
        pre:<int>, 每页多少条

    """

    data = search_process()
    return response_format(data)


@api.route('/search/logs', methods=['GET', "DELETE"])
@permission_required(use_default=False)
def api_search_logs():
    """
    GET:
        获取用户的搜索历史
        number:<int>, 获取最后的多少条历史， 默认10， 最大20

    """
    if request.c_method == "GET":
        data = get_search_logs()
    elif request.c_method == "DELETE":
        data = clear_search_logs()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
