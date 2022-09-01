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
from apps.modules.post.process.user_post import post_issue, post_restore, post_delete


@api.route('/user/post', methods=['POST', 'PUT', 'PATCH', 'DELETE'])
@osr_login_required
@permission_required(use_default=False)
def api_user_post_op():
    """
    POST:
        内容发布
        title:<str>, 标题
        content:<str>, 内容(比如:富文本的html内容),将会保存到数据库中
        conetent_text:<str>, 纯文本内容
        editor:<str>, 使用的编辑器类型, "markdown" or "rich_text"
        tags:<array>, 标签
        category:<str>, post category id. post分类
        cover_url:<str>,文章封面图url,默认为空
        issue_way:<str>, 可选'issue' or 'save'.　发布或者保存为草稿


    PUT or PATCH:
        1.内容修改
        id:<str>, 编辑已有的文章需要传入id, 新建文章不需要
        title:<str>, 标题
        content:<str>, 内容(比如:富文本的html内容),将会保存到数据库中
        conetent_text:<str>, 纯文本内容
        editor:<str>, 使用的编辑器类型, "markdown" or "rich_text"
        tags:<array>, 标签
        category:<str>, post category id. post分类
        issue_way:<str>, 可选'issue' or 'save'.　发布或者保存为草稿

        2.恢复回收站的post
        op:<str>, restore
        ids:<array>, posts id

    DELETE:
        删除post
        ids:<array>, posts id
        recycle:<int>,1 or 0,　1：则移入回收站, 0: 则直接标记为永久删除, 管理员才可见

    """
    if request.c_method == "POST":
        data = post_issue()
    elif request.c_method in ["PUT", "PATCH"]:
        if request.argget.all('op') == "restore":
            data = post_restore()
        else:
            data = post_issue()
    elif request.c_method == "DELETE":
        data = post_delete()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
