#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from bson import ObjectId
from copy import deepcopy
from flask_babel import gettext
import time
from flask_login import current_user
from werkzeug.exceptions import abort
from apps.app import mdbs, cache
from apps.modules.user.process.user_profile_process import get_user_public_info
from apps.utils.format.obj_format import objid_to_str
from apps.utils.paging.paging import datas_paging
from apps.utils.upload.file_up import file_del
from apps.utils.upload.get_filepath import get_file_url
from apps.core.utils.get_config import get_config


def get_posts_pr(
        field=None,
        page=1,
        pre=10,
        status="is_issued",
        sort=None,
        time_range=None,
        matching_rec=None,
        keyword=None,
        other_filter=None,
        is_admin=False,
        *args,
        **kwargs):
    """
    获取一些指定的post
    :param field:
    :param page:
    :param pre:
    :param status:
    :param sort:
    :param time_range:
    :param matching_rec:
    :param keyword:
    :param other_filter:
    :param is_admin: 是admin用户获取, 可以获取未公开的post
    :param args:
    :param kwargs:
    :return:
    """

    if pre > get_config("post", "NUM_PAGE_MAX"):
        data = {"msg": gettext('The "pre" must not exceed the maximum amount'),
                "msg_type": "e", "custom_status": 400}
        return data
    query_conditions = {}
    if other_filter:
        query_conditions = deepcopy(other_filter)

    if status and status != "is_issued" and not is_admin:
        # 非admin用户获取未公开post, 需要认证
        if not current_user.is_authenticated:
            # 未登录用户
            abort(401)
        elif "user_id" in query_conditions:
            if query_conditions["user_id"] != current_user.str_id:
                # 要获取的user_id不是当前用户
                abort(401)
        else:
            # 默认获取当前用户
            query_conditions["user_id"] = current_user.str_id
    # 是否使用缓存, 按以下条件决定
    use_cache = False
    if status == "no_issued":
        query_conditions['$or'] = [
            {
                'issued': 0}, {
                'is_delete': 1}, {
                'audited': 1, 'audit_score': {
                    "$gte": get_config(
                        "content_inspection", "ALLEGED_ILLEGAL_SCORE")}}, ]
    elif status == "draft":
        query_conditions['issued'] = 0
        query_conditions['is_delete'] = 0

    elif status == "not_audit":
        query_conditions['issued'] = 1
        query_conditions['is_delete'] = 0
        # 没有审核, 而且默认评分涉嫌违规的
        query_conditions['audited'] = 0
        query_conditions['audit_score'] = {
            "$gte": get_config(
                "content_inspection",
                "ALLEGED_ILLEGAL_SCORE")}

    elif status == "unqualified":
        query_conditions['issued'] = 1
        query_conditions['is_delete'] = 0
        query_conditions['audited'] = 1
        query_conditions['audit_score'] = {
            "$gte": get_config(
                "content_inspection",
                "ALLEGED_ILLEGAL_SCORE")}

    elif status == "recycle":
        query_conditions['is_delete'] = 1

    elif status == "user_remove":
        query_conditions['is_delete'] = {"$in": [2, 3]}

    else:
        if not is_admin:
            if not current_user.is_authenticated:
                # 获取公开发布内容
                use_cache = True
            elif not other_filter:
                use_cache = True
            elif other_filter and ("user_id" not in other_filter or other_filter["user_id"] != current_user.str_id):
                # 如果没有查询中没有指定用户,或者指定的用户不是当前用户, 则使用缓存功能
                use_cache = True

        query_conditions['issued'] = 1
        query_conditions['is_delete'] = 0
        query_conditions['audit_score'] = {
            "$lt": get_config(
                "content_inspection",
                "ALLEGED_ILLEGAL_SCORE")}

    if keyword:
        keyword = {"$regex": keyword, "$options": "$i"}
        query_conditions["$or"] = [{"title": keyword},
                                   {"content": keyword},
                                   {"category": keyword},
                                   {"tag": keyword}
                                   ]
    # sort
    if sort:
        for i, srt in enumerate(sort):
            sort[i] = (list(srt.keys())[0], list(srt.values())[0])
    else:
        sort = [("issue_time", -1), ("update_time", -1)]

    # time_range
    if time_range:
        now_time = time.time()
        gt_time = (now_time - 86400 * (time_range - 1)) - now_time % 86400
        query_conditions["issue_time"] = {'$gt': gt_time}

    get_userinfo = kwargs.get("get_userinfo", True)

    if use_cache:
        return get_posts_use_cache(query_conditions=query_conditions,
                                   field=field, sort=sort,
                                   pre=pre,
                                   page=page,
                                   get_userinfo=get_userinfo)
    else:
        return get_posts_query(query_conditions=query_conditions,
                               field=field, sort=sort,
                               pre=pre,
                               page=page,
                               get_userinfo=get_userinfo)


@cache.cached(timeout=get_config("post", "GET_POST_CACHE_TIME_OUT"))
def get_posts_use_cache(
        query_conditions,
        field,
        sort,
        pre,
        page,
        get_userinfo):
    """
    调用get_posts_query, 主要提供缓存功能
    :param query_conditions:
    :param field:
    :param sort:
    :param pre:
    :param page:
    :param get_userinfo:
    :return:
    """
    return get_posts_query(
        query_conditions,
        field,
        sort,
        pre,
        page,
        get_userinfo)


def get_posts_query(query_conditions, field, sort, pre, page, get_userinfo):
    """
    提供查询条件等获取文章
    :param query_conditions:
    :param field:
    :param sort:
    :param pre:
    :param page:
    :param get_userinfo:
    :return:
    """
    data = {}
    if field:
        ps = mdbs["web"].db.post.find(query_conditions, field)
    else:
        ps = mdbs["web"].db.post.find(query_conditions)

    data_cnt = ps.count(True)
    posts = list(ps.sort(sort).skip(pre * (page - 1)).limit(pre))
    for post in posts:
        post = objid_to_str(post, ["_id", "user_id", "audit_user_id"])
        # image
        if "cover_url" in post and post["cover_url"]:
            post["cover_url"] = get_file_url(post["cover_url"])
        if "imgs" in post and len(post["imgs"]):

            for i, img in enumerate(post["imgs"]):
                post["imgs"][i] = get_file_url(img)

        if "user_id" not in query_conditions.keys() and get_userinfo:
            s, r = get_user_public_info(
                user_id=post["user_id"],
                is_basic=False,
                current_user_isauth=current_user.is_authenticated)
            if s:
                post["user"] = r
            else:
                post['user'] = {}
        # category
        if "category" in post and post["category"]:
            post["category"] = str(post["category"])
            category = mdbs["web"].db.category.find_one(
                {"_id": ObjectId(post["category"])})
            if category:
                post["category_name"] = category["name"]

    data["posts"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=posts)
    return data


def get_post_pr(
        post_id="",
        other_filter=None,
        is_admin=False,
        *args,
        **kwargs):
    """
    获取一个Post
    :param post_id:
    :param other_filter:
    :param is_admin: 是admin用户获取, 可以获取未公开的post
    :param args:
    :param kwargs:
    :return:
    """
    data = {}
    query_conditions = {}
    if isinstance(other_filter, dict):
        query_conditions = deepcopy(other_filter)

    query_conditions["_id"] = ObjectId(post_id)

    post = mdbs["web"].db.post.find_one(query_conditions)
    if post:
        if not is_admin:
            if not post["issued"] or post["is_delete"] or post["audit_score"] >= get_config(
                    "content_inspection", "ALLEGED_ILLEGAL_SCORE"):
                # 未公开的
                if not current_user.is_authenticated or current_user.str_id != str(
                        post["user_id"]):
                    # 没有权限访问
                    abort(401)

        post = objid_to_str(post, ["_id", "user_id", "audit_user_id"])
        post["cover_url"] = get_file_url(post["cover_url"])
        imgs_l = len(post["imgs"])
        if imgs_l:
            for i, img in enumerate(post["imgs"]):
                post["imgs"][i] = get_file_url(img)

        s, r = get_user_public_info(user_id=post["user_id"],
                                    is_basic=False,
                                    current_user_isauth=current_user.is_authenticated)
        if s:
            post["user"] = r
        data["post"] = post
        if "category" in post and post["category"]:
            category = mdbs["web"].db.category.find_one(
                {"_id": ObjectId(str(post["category"]))})
            if category:
                data["post"]["category_name"] = category["name"]

        if current_user.is_authenticated and current_user.str_id in post["like_user_id"]:
            post["like_it_already"] = True
    else:
        abort(404)
    return data


def delete_post(ids=[]):
    """
    完全删除一篇文章
    :return:
    """
    posts = mdbs["web"].db.post.find(
        {"_id": {"$in": ids}, "is_delete": {"$in": [2, 3]}}, {"imgs": 1})
    rm_pids = []
    if posts.count(True):
        for post in posts:
            # 删用户的post喜欢标记
            mdbs["user"].db.user_like.update_many({"type": "post", "values": str(post["_id"])},
                                              {"$pull": {"values": str(post["_id"])}})

            # 删图片
            for img in post["imgs"]:
                file_del(img)

            if "cover_url" in post:
                file_del(post["cover_url"])
            # 删post pv
            mdbs["web"].db.access_record.delete_many({"post_id": post["_id"]})

            # 删除评论
            comments = mdbs["web"].db.comment.find(
                {"_target_id": post["_id"]}, {"_id": 1})
            mdbs["web"].db.comment.delete_many({"_target_id": post["_id"]})
            # 删用户的评论喜欢标记
            for comment in comments:
                mdbs["user"].db.user_like.update_many({"type": "comment", "values": str(
                    comment["_id"])}, {"$pull": {"values": str(comment["_id"])}})
            rm_pids.append(post["_id"])

    r = mdbs["web"].db.post.delete_many(
        {"_id": {"$in": rm_pids}, "is_delete": {"$in": [2, 3]}})
    if r.deleted_count:
        data = {"msg": gettext("Removed from the database, {}").format(
            r.deleted_count), "msg_type": "s", "custom_status": 204}
    else:
        data = {"msg": gettext("No match to relevant data"),
                "msg_type": "w", "custom_status": 400}

    return data
