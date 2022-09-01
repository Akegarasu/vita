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
from apps.modules.message.process.sys_message import get_sys_message, delete_sys_message


@api.route('/admin/message/email', methods=['GET', 'DELETE'])
@api.route('/admin/message/sms', methods=['GET', 'DELETE'])
@osr_login_required
@permission_required()
def api_adm_sys_message():
    """
    GET:
        获取系统发送出去的邮件或短信记录
        status:<str>, 状态, normal, abnormal, error
        pre:<int>,每页获取几条数据,默认10
        page:<int>,第几页,默认1
    DELETE:
        删除消息(此接口只能删除由系统发出的消息user_id==0的)
        ids:<array>,消息id
    :return:
    """

    if request.c_method == "GET":
        data = get_sys_message()

    elif request.c_method == "DELETE":
        data = delete_sys_message()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
