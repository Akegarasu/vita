#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from copy import deepcopy
from flask_babel import gettext
from flask_login import current_user
from apps.utils.format.obj_format import objid_to_str
from apps.utils.format.time_format import time_to_utcdate
from apps.utils.paging.paging import datas_paging
from apps.app import mdbs
from apps.core.utils.get_config import get_config


def find_comments(
        query_conditions={},
        page=1,
        pre=10,
        sort=None,
        keyword="",
        status="is_issued",
        *args,
        **kwargs):

    data = {}
    if pre > get_config("comment", "NUM_PAGE_MAX"):
        data = {"msg": gettext('The "pre" must not exceed the maximum amount'),
                "msg_type": "e", "custom_status": 400}
        return data

    query_conditions = deepcopy(query_conditions)

    if status == "not_audit":
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

    elif status == "user_remove":
        query_conditions['is_delete'] = {"$in": [1, 2]}

    else:
        query_conditions['issued'] = 1
        query_conditions['is_delete'] = 0
        query_conditions['audit_score'] = {
            "$lt": get_config(
                "content_inspection",
                "ALLEGED_ILLEGAL_SCORE")}

    if keyword:
        keyword = {"$regex": keyword, "$options": "$i"}
        query_conditions["content"] = keyword

    cs = mdbs["web"].db.comment.find(query_conditions)
    data_cnt = cs.count(True)

    # sort
    if sort:

        for i, srt in enumerate(sort):
            sort[i] = (list(srt.keys())[0], list(srt.values())[0])

    else:
        sort = [("issue_time", -1)]

    comments = list(cs.sort(sort).skip(pre * (page - 1)).limit(pre))
    comments = recursive_find_comment(comments)

    data["comments"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=comments)
    return data


def recursive_find_comment(comments):

    for comment in comments:
        comment = objid_to_str(
            comment, [
                "_id", "user_id", "audit_user_id", ""])
        comment["date"] = time_to_utcdate(
            time_stamp=comment["issue_time"],
            tformat="%Y-%m-%d %H:%M")
        if current_user.is_authenticated:
            r = mdbs["user"].db.user_like.find_one(
                {"user_id": current_user.str_id, "type": "comment", "values": comment["_id"]})
            if r:
                comment["like_it_already"] = True
        # 评论下面的所有回复
        query_conditions = {}
        query_conditions['issued'] = 1
        query_conditions['is_delete'] = 0
        query_conditions['audit_score'] = {
            "$lt": get_config(
                "content_inspection",
                "ALLEGED_ILLEGAL_SCORE")}
        query_conditions["reply_id"] = comment["_id"]
        reply_comments = mdbs["web"].db.comment.find(
            query_conditions).sort([("issue_time", -1)])
        if reply_comments.count(True):
            comment["reply"] = objid_to_str(
                list(reply_comments), [
                    "_id", "user_id", "audit_user_id"])
            comment["reply"] = recursive_find_comment(comment["reply"])

    return comments
