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
from apps.modules.post.process.adm_post import adm_get_post, \
    adm_get_posts, adm_post_audit, adm_post_restore, \
    adm_post_delete


@api.route('/admin/post', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@osr_login_required
@permission_required()
def api_adm_post():
    """
    GET:
        1. 根据条件获取文章
        sort:<array>,排序, 1表示升序, -1表示降序.如:
            按时间降序 [{"issue_time":-1},{"update_time",-1}]
            按时间升序 [{"issue_time", 1},{"update_time",1}]
            先后按赞(like)数降序, 评论数降序,pv降序, 发布时间降序
             [{"like", -1}, {"comment_num", -1}, {"pv", -1},{"issue_time", -1}];
            默认时按时间降序, 也可以用其他字段排序
        page:<int>,第几页，默认第1页
        pre:<int>, 每页查询多少条
        status:<int> , "is_issued"（正常发布） or "draft"（草稿） or "not_audit"（等待审核） or "unqualified"（未通过审核） or "recycle"(用户的回收站) or "user_remove"
            （user_remove是指用户永久删除或被管理删除的）
        keyword:<str>, Search keywords, 搜索的时候使用
        fields:<array>, 需要返回的文章字段,如["title"]
        unwanted_fields:<array>, 不能和fields参数同时使用,不需要返回的文章字段,如["content"]
        :return:

        2.获取一篇文章
        post_id:<str>,post id
        status:<str>,状态, 可以是"is_issued" or "draft" or "not_audit" or "unqualified" or "recycle"

    PATCH or PUT:
        1.人工审核post
        op:<str>, 为"audit"
        ids:<str>, posts id
        score:<int>, 0-100分

        2.恢复post, 只能恢复管理员移入待删除的文章is_delete为3的post
        op:<str>, 为"restore"
        ids:<array>, posts id

    DELETE:
        删除post
        ids:<array>, posts id
        pending_delete:<int>, 1: 标记is_delete为3, 对于post属于的用户永久删除, 0:从数据库删除数据
        :return:
    """

    if request.c_method == "GET":
        if request.argget.all('post_id'):
            data = adm_get_post()
        else:
            data = adm_get_posts()

    elif request.c_method in ["PUT", "PATCH"]:
        if request.argget.all("op") == "audit":
            data = adm_post_audit()
        elif request.argget.all("op") == "restore":
            data = adm_post_restore()

    elif request.c_method == "DELETE":
        data = adm_post_delete()

    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
