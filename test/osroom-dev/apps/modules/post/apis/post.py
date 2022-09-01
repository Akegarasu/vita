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
from apps.modules.post.process.get_post_tags import get_tags
from apps.modules.post.process.post import get_post, get_posts, post_like


@api.route('/post/tags', methods=['GET'])
@permission_required(use_default=False)
def api_post_tags():
    """
    GET:
        获取文章tag
        last_days:<int>, 获取最近几天时间的文章的tag
        sort:<array>,文章排序规则,优先获取排在前面的文章的标签, 1表示升序, -1表示降序.如:
            先后按赞(like)数降序, 评论数降序,pv降序, 发布时间降序
            [{"like": -1}, {"comment_num": -1}, {"pv": -1}]
            默认时按tag_cnt, like, comment_num 多个降序
            可选字段有like, pv, comment_num, tag_cnt
        user_id:<str>, 获取单个用户的文章tag, 默认是全部用户的文章tag
        limit:<int>, 获取多少个tag
    :return:
    """
    if request.c_method == "GET":
        data = get_tags()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)


@api.route('/post', methods=['GET'])
@permission_required(use_default=False)
def api_post():
    """
    GET:
        1.获取一篇文章
        post_id:<str>,post id

        2.根据条件获取文章
        sort:<array>,排序, 1表示升序, -1表示降序.如:
            按时间降序 [{"issue_time":-1},{"update_time":-1}]
            按时间升序 [{"issue_time": 1},{"update_time": 1}]
            先后按赞(like)数降序, 评论数降序,pv降序, 发布时间降序
            [{"like": -1}, {"comment_num": -1}, {"pv": -1},{"issue_time": -1}]
            默认时按时间降序, 也可以用其他字段排序
        status:<int> , "is_issued"（正常发布） or "draft"（草稿） or "not_audit"（等待审核） or "unqualified"（未通过审核） or "recycle"(用户的回收站) or "user_remove"
            （user_remove是指用户永久删除或被管理删除的）

        matching_rec:<str>,可选，提供一段内容, 匹配一些文章推荐
        time_range:<int>,可选,单位为天,比如最近7天的文章
        page:<int>,第几页，默认第1页
        pre:<int>, 每页查询多少条
        keyword:<str>, Search keywords, 搜索使用
        fields:<array>, 需要返回的文章字段,如["title"]
        unwanted_fields:<array>, 不能和fields参数同时使用,不需要返回的文章字段,如["user_id"]
        user_id:<str>, 如需获取指定用户的post时需要此参数
        category_id:<str>, 获取指定文集的post时需要此参数
        tag:<str>, 获取存在此tag的posts时需要此参数

    """

    if request.c_method == "GET":
        if request.argget.all('post_id'):
            data = get_post()
        else:
            data = get_posts()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)


@api.route('/post', methods=['PUT'])
@osr_login_required
@permission_required(use_default=False)
def api_post_op():
    """
    PUT:
        喜欢文章
        action:<str>, 可以是like(点赞文章)
        id:<str>, post id

    """
    if request.c_method == "PUT":
        if request.argget.all('action') == "like":
            data = post_like()
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
