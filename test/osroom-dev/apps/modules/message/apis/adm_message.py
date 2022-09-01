#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from apps.core.flask.login_manager import osr_login_required
from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.message.process.user_message import get_user_msgs, delete_user_msgs


@api.route('/admin/message/on-site', methods=['GET', 'PUT', 'DELETE'])
@osr_login_required
@permission_required()
def api_adm_message():
    """
    GET:
        获取用户消息
        is_sys_msg:<int>,获取系统消息? 1表示是, 0表示否
        pre:<int>,每页获取几条数据,默认10
        page:<int>,第几页,默认1
        type:<array>,消息类型, 比如["notice", "comment", "audit"]
    DELETE:
        删除消息(此接口只能删除由系统发出的消息user_id==0的)
        ids:<array>,消息id
    :return:
    """

    if request.c_method == "GET":
        data = get_user_msgs(is_admin=True)

    elif request.c_method == "DELETE":
        data = delete_user_msgs(is_admin=True)
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
