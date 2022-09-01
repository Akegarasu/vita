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
from apps.modules.comments.process.comment import comments, comment_issue, comment_delete, comment_like


@api.route('/comment', methods=['GET'])
@permission_required(use_default=False)
def api_get_comment():
    """
    GET:
        获取文章的评论
        target_id:<str>, 目标id,比如文章post id
        target_type:<str>, 目标类型,比如文章就是"post"
        status:<str>,"is_issued"（正常发布） or "not_audit"（等待审核） or "unqualified"（未通过审核） or "user_remove"(用户删除的)

        sort:<array>,排序, 1表示升序, -1表示降序.如:
            按时间降序 [{"issue_time":-1}]
            按时间升序 [{"issue_time": 1}]
            先后按赞(like)数降序, 评论数降序,pv降序, 发布时间降序
            [{"like": -1},{"issue_time": -1}]
            默认时按时间降序, 也可以用其他字段排序

        page:<int>,第几页，默认第1页
        pre:<int>, 每页查询多少条, 默认是config.py配制文件中配制的数量
        :return:

    """
    data = comments()
    return response_format(data)


@api.route('/comment', methods=['POST', 'PUT', 'PATCH', 'DELETE'])
@permission_required(use_default=False)
def api_comment_op():
    """
    POST:
        评论发布
        target_id:<str>, 目标id,比如文章post id
        target_type:<str>, 目标类型,比如文章就是"post"

        reply_id:<str>, 被回复的comment id.
        如果是回复评论中的评论,如:在评论a下面有一个评论a1，我需要回复a1, 这个时候需要提供的reply_id依然是a评论的，　而不是a1的

        reply_user_id:<str>, 被回复的comment 的用户的user id，
        如果是回复评论中的评论,如:在评论a下面有一个评论a1，我需要回复a1, 这个时候需要提供的reply_user_id是a１评论的

        reply_username:<str>, 被回复的comment 的用户的username，
        如果是回复评论中的评论,如:在评论a下面有一个评论a1，我需要回复a1, 这个时候需要提供的reply_username是a１评论的

        content:<str>, 内容(比如:富文本的html内容),将会保存到数据库中

        如果是游客评论,则需要以下两个参数(需要再后台配置中开启游客评论开关):
        username:<str>, 游客昵称
        email:<str>,游客邮箱
        :return:

    DELETE:
        评论删除
        ids:<array>, comment ids
    """
    if request.c_method == "POST":
        data = comment_issue()

    elif request.c_method == "DELETE":
        data = comment_delete()

    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)


@api.route('/comment/like', methods=['PUT'])
@osr_login_required
@permission_required(use_default=False)
def api_comment_like():
    """
    PUT:
        给评论点赞
        id:<str>
    :return:
    """
    data = comment_like()
    return response_format(data)
