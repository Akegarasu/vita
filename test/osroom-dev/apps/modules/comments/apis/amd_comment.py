#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from apps.core.flask.login_manager import osr_login_required
from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.response import response_format
from apps.core.flask.permission import permission_required
from apps.modules.comments.process.adm_comment import adm_comments, adm_comment_audit, adm_comment_restore, \
    adm_comment_delete


@api.route('/admin/comment', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@osr_login_required
@permission_required()
def api_adm_comment():
    """
    GET:
        获取评论
        status:<str>,"is_issued"（正常发布） or "not_audit"（等待审核） or "unqualified"（未通过审核） or "user_remove"(用户删除的)
        keyword:<str>,搜索关键字

        sort:<array>,排序, 1表示升序, -1表示降序.如:
            按时间降序 [{"issue_time":-1}]
            按时间升序 [{"issue_time": 1}]
            先后按赞(like)数降序, 评论数降序,pv降序, 发布时间降序
            [{"like": -1},{"issue_time": -1}]
            默认时按时间降序, 也可以用其他字段排序

        page:<int>,第几页，默认第1页
        pre:<int>, 每页查询多少条, 默认是config.py配制文件中配制的数量
        :return:
    PATCH or PUT:
        1.人工审核comment, 带上参数score
        op:<str>, "audit"
        ids:<array>, comment id
        score:<int>, 0-10分

        2.恢复comment, 只能恢复管理员移入待删除的comment, is_delete为2的comment
        op:<str>,  "restore"
        ids:<array>, comment id

    DELETE:
        删除comment
        ids:<array>, comment id
        pending_delete:<int>, 1: is_delete为2, 标记为永久删除, 0:从数据库删除数据
        :return:
    """
    if request.c_method == "GET":
        data = adm_comments()

    elif request.c_method in ["PUT", "PATCH"]:
        if request.argget.all("op") == "audit":
            data = adm_comment_audit()
        elif request.argget.all("op") == "restore":
            data = adm_comment_restore()

    elif request.c_method == "DELETE":
        data = adm_comment_delete()

    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
