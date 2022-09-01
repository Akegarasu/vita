#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import time

from celery_once import QueueOnce
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.app import celery, mdbs
from apps.core.flask.reqparse import arg_verify
from apps.modules.post.process.post_process import get_posts_pr
from apps.utils.format.obj_format import str_to_num
from apps.utils.format.time_format import time_to_utcdate
from apps.utils.paging.paging import datas_paging
from apps.utils.upload.get_filepath import get_avatar_url


def search_process():
    """
    搜索(暂不支持全文搜索)
    只能搜索文章, 用户
    :return:
    """

    keyword = request.argget.all('keyword')
    target = request.argget.all('target')
    page = str_to_num(request.argget.all('page', 1))
    pre = str_to_num(request.argget.all('pre', 10))

    s, r = arg_verify(reqargs=[(gettext("keyword"), keyword)], required=True)
    if not s:
        return r
    if current_user.is_authenticated:
        user_id = current_user.str_id
    else:
        user_id = ""
    search_logs.apply_async(
        kwargs={
            "user_id": user_id,
            "keyword": keyword
        }
    )
    data = {"posts": {}, "users": {}}
    # post
    if not target or target == "post":
        data["posts"] = {}
        data["posts"]["items"] = get_posts_pr(
            field={
                "title": 1,
                "issue_time": 1,
                "brief_content": 1},
            page=page,
            pre=pre,
            status="is_issued",
            sort=None,
            time_range=None,
            matching_rec=None,
            keyword=keyword,
            other_filter=None,
            is_admin=False,
            get_userinfo=False)["posts"]
        data["posts"]["kw"] = keyword

    if not target or target == "user":
        # user
        data["users"] = {"kw": keyword, "items": []}
        query_conditions = {
            "is_delete": {
                "$in": [
                    False, 0]}, "active": {
                "$in": [
                    True, 1]}}
        keyword = {"$regex": keyword, "$options": "$i"}
        query_conditions["$or"] = [{"username": keyword},
                                   {"email": keyword},
                                   {"custom_domain": keyword}
                                   ]
        us = mdbs["user"].db.user.find(
            query_conditions, {
                "_id": 1, "username": 1, "avatar_url": 1, "custom_domain": 1, "gender": 1, })

        data_cnt = us.count(True)
        users = list(us.skip(pre * (page - 1)).limit(pre))
        for user in users:
            user['_id'] = str(user['_id'])
            user["avatar_url"]["url"] = get_avatar_url(user["avatar_url"])

        data["users"]["items"] = datas_paging(
            pre=pre, page_num=page, data_cnt=data_cnt, datas=users)
    return data


@celery.task(base=QueueOnce, once={'graceful': True})
def search_logs(user_id, keyword):
    ut = time.time()
    month = time_to_utcdate(ut, "%Y%m")
    day = time_to_utcdate(ut, "%Y%m%d")
    mdbs["web"].dbs["search_logs"].update_one(
        {
            "user_id": user_id,
            "search": keyword
        },
        {
            "$inc": {"num_of_search": 1},
            "$addToSet": {"days": day, "months": month},
            "$set": {
                "lasted_time": ut,
                "status": "normal"
            }
        },
        upsert=True
    )


def get_search_logs():
    number = str_to_num(request.argget.all('number', 10))
    if not number:
        number = 10
    if number > 20:
        number = 20
    user_logs = []
    if current_user.is_authenticated:
        user_id = current_user.str_id
        user_logs = mdbs["web"].dbs["search_logs"].find(
            {
                "user_id": user_id,
                "status": "normal"
            },
            {
                "_id": 0
            }
        ).sort([("lasted_time", -1)]).limit(number)
        user_logs = list(user_logs)
        user_logs = sorted(user_logs, key=lambda x: -x["lasted_time"])
    return {
        "logs": user_logs
    }


def clear_search_logs():
    if current_user.is_authenticated:
        user_id = current_user.str_id
        mdbs["web"].dbs["search_logs"].update_many(
            {
                "user_id": user_id
            },
            {
                "$set": {"status": "deleted"}
            }
        )
    return {
        "msg": gettext("Cleaned"),
        "msg_type": "s",
        "custom_status": 204
    }
