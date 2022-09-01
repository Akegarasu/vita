#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from bson.objectid import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user
from apps.app import mdbs
from apps.modules.post.process.post_statistical import post_pv
from apps.modules.post.process.post_process import get_posts_pr, get_post_pr
from apps.core.utils.get_config import get_config
from apps.utils.format.obj_format import json_to_pyseq, str_to_num


def get_post(post_id=None):

    if not post_id:
        post_id = request.argget.all('post_id')

    sid = request.cookies["session"]
    post_pv.apply_async(
        kwargs={
            "post_id": post_id,
            "sid": sid
        }
    )
    data = get_post_pr(post_id=post_id)
    return data


def get_posts(page=None):
    if not page:
        page = str_to_num(request.argget.all('page', 1))
    pre = str_to_num(request.argget.all('pre', get_config("post", "NUM_PAGE")))
    sort = json_to_pyseq(request.argget.all('sort'))
    status = request.argget.all('status', 'is_issued')
    matching_rec = request.argget.all('matching_rec')
    time_range = int(request.argget.all('time_range', 0))
    keyword = request.argget.all('keyword', '').strip()
    fields = json_to_pyseq(request.argget.all('fields'))
    unwanted_fields = json_to_pyseq(request.argget.all('unwanted_fields'))
    user_id = request.argget.all('user_id')
    category_id = request.argget.all('category_id')
    tag = request.argget.all('tag')

    # 不能同时使用fields 和 unwanted_fields
    temp_field = {}
    if fields:
        for f in fields:
            temp_field[f] = 1
    elif unwanted_fields:
        for f in unwanted_fields:
            temp_field[f] = 0

    other_filter = {}
    if user_id:
        # 获取指定用户的post
        other_filter["user_id"] = user_id

    # 如果category_id为None， 则获取全部分类文章
    if category_id:

        try:
            ObjectId(category_id)
            # 指定分类
            other_filter["category"] = category_id
        except BaseException:
            # 默认文集
            other_filter["category"] = None

    if tag:
        other_filter["tags"] = tag
    data = get_posts_pr(
        page=page,
        field=temp_field,
        pre=pre,
        sort=sort,
        status=status,
        time_range=time_range,
        matching_rec=matching_rec,
        keyword=keyword,
        other_filter=other_filter)
    return data


def post_like():

    tid = request.argget.all('id')
    like = mdbs["user"].db.user_like.find_one(
        {"user_id": current_user.str_id, "type": "post"})
    if not like:
        user_like = {
            "values": [],
            "type": "post",
            "user_id": current_user.str_id
        }
        mdbs["user"].db.user_like.insert_one(user_like)
        r1 = mdbs["user"].db.user_like.update_one(
            {"user_id": current_user.str_id, "type": "post"}, {"$addToSet": {"values": tid}})
        r2 = mdbs["web"].db.post.update_one({"_id": ObjectId(tid)}, {
                                        "$inc": {"like": 1}, "$addToSet": {"like_user_id": current_user.str_id}})

    else:
        if tid in like["values"]:
            like["values"].remove(tid)
            r2 = mdbs["web"].db.post.update_one({"_id": ObjectId(tid)}, {
                                            "$inc": {"like": -1}, "$pull": {"like_user_id": current_user.str_id}})
        else:
            like["values"].append(tid)
            r2 = mdbs["web"].db.post.update_one({"_id": ObjectId(tid)}, {
                                            "$inc": {"like": 1}, "$addToSet": {"like_user_id": current_user.str_id}})
        r1 = mdbs["user"].db.user_like.update_one({"user_id": current_user.str_id, "type": "post"},
                                              {"$set": {"values": like["values"]}})

    if r1.modified_count and r2.modified_count:
        data = {"msg": gettext("Success"), "msg_type": "s", "custom_status": 201}
    else:
        data = {"msg": gettext("Failed"), "msg_type": "w", "custom_status": 400}
    return data
