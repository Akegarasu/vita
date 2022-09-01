#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from apps.core.flask.login_manager import osr_login_required
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.report.process.basic_access import get_post_access, get_comment_access, get_user_access, get_message, \
    get_plugin, get_media, get_inform_data
from apps.utils.format.obj_format import json_to_pyseq



@api.route('/admin/report/basic', methods=['GET'])
@osr_login_required
@permission_required()
def api_basic_report():
    """
    GET:
        获取网站的最基本报表数据
        project:<array>,默认全部,可以是post, comment, user, message, plugin, media, inform

    """
    project = json_to_pyseq(request.argget.all('project', []))

    data = {}
    if "post" in project or not project:
        data["post"] = get_post_access()

    if "comment" in project or not project:
        data["comment"] = get_comment_access()

    if "user" in project or not project:
        data["user"] = get_user_access()

    if "message" in project or not project:
        data["message"] = get_message()
    if "plugin" in project or not project:
        data["plugin"] = get_plugin()
    if "media" in project or not project:
        data["media"] = get_media()
    if "inform" in project or not project:
        data["inform"] = get_inform_data()
    return response_format(data)
