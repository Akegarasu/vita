#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.core.flask.login_manager import osr_login_required
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.message.process.send_msg import send_msg


@api.route('/admin/message/send', methods=['POST'])
@osr_login_required
@permission_required()
def api_adm_send_msg():
    """
    POST
        发送消息
        title:<title>,标题
        content:<str>,正文
        content_html:<str>,正文html
        send_type:<array>,发送类型on_site, email, sms . 如:["email"], 也可以同时发送多个个["email", "on_site"]
        username:<array>, 接收信息的用户名, 如["test", "test2"]
    :return:
    """
    data = send_msg()
    return response_format(data)
