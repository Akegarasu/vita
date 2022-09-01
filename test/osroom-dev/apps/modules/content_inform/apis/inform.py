#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request

from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.content_inform.process.inform import content_inform


@api.route('/inform/content', methods=['PUT'])
@permission_required(use_default=False)
def api_content_inform():
    """
    PUT:
        内容违规举报
        ctype:<str>, 内容的类型可选:post(文章), comment(评论), media(多媒体), user(用户)
        cid:<str>, 内容的id
        category:<str>, 举报内容违规类型, 可选: ad, junk_info, plagiarize, other
        details：<str>, 违规详情(选填)


    """
    if request.c_method == "PUT":
        data = content_inform()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
