#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.setting.process.session_set import language_set


@api.route('/session/language-set', methods=['PUT'])
@permission_required(use_default=False)
def api_language_set():
    """
    PUT :
        修改当前语言
        language:<str>, 如en_US, zh_CN
    :return:
    """
    data = language_set()
    return response_format(data)
