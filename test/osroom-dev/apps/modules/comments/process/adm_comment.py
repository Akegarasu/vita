#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user
from apps.modules.comments.process.comment import find_comments
from apps.modules.message.process.user_message import insert_user_msg
from apps.utils.format.obj_format import json_to_pyseq
from apps.app import mdbs
from apps.core.utils.get_config import get_config


def adm_comments():

    sort = json_to_pyseq(request.argget.all('sort'))
    status = request.argget.all('status', "is_issued")
    keyword = request.argget.all('keyword', "")
    page = int(request.argget.all('page', 1))
    pre = int(request.argget.all('pre', 10))
    basic_query = {'issued': 1, 'is_delete': 0}

    data = find_comments(
        query_conditions=basic_query,
        page=page,
        pre=pre,
        sort=sort,
        keyword=keyword,
        status=status)
    return data


def adm_comment_audit():

    ids = json_to_pyseq(request.argget.all('ids', []))
    score = int(request.argget.all("score", 0))

    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)

    r = mdbs["web"].db.comment.update_many({
                                "_id": {"$in": ids}},
                               {"$set": {
                                        "audited": 1,
                                        "audit_score": score,
                                        "audit_way": "artificial",
                                        "audit_user_id": current_user.str_id}})
    if r.modified_count:

        if score >= get_config("content_inspection", "ALLEGED_ILLEGAL_SCORE"):

            # 审核不通过，给用户通知
            coms = mdbs["web"].db.comment.find({"_id": {"$in": ids}}, {
                                           "user_id": 1, "content": 1, "_id": 1, "audit_score": 1})
            for com in coms:
                msg_content = {"text": com["content"]}
                insert_user_msg(
                    user_id=com["user_id"],
                    ctype="notice",
                    label="comment",
                    title=gettext("Comment on alleged violations"),
                    content=msg_content,
                    target_id=str(
                        com["_id"]),
                    target_type="comment")
        else:
            # 审核通过, 给被评论对象通知
            coms = mdbs["web"].db.comment.find({"_id": {"$in": ids}})
            for com in coms:
                msg_content = {
                    "id": str(com["_id"]),
                    "user_id": str(com["user_id"]),
                    "username": com["username"],
                    "text": com["content"]}

                user_ids = [com["target_user_id"]]
                if "reply_id" in com:
                    user_ids.append(com["reply_id"])
                    msg_content["reply_id"] = com["reply_id"],
                    msg_content["reply_user_id"] = com["reply_user_id"],
                    msg_content["reply_username"] = com["reply_username"]

                insert_user_msg(
                    user_id=user_ids,
                    ctype="notice",
                    label="comment",
                    title=com["target_brief_info"],
                    content=msg_content,
                    target_id=com["target_id"],
                    target_type=com["type"])

        data = {"msg": gettext("Submitted successfully, {}").format(
            r.modified_count), "msg_type": "s", "custom_status": 201}
    else:
        data = {
            "msg": gettext("Submitted failed"),
            "msg_type": "w",
            "custom_status": 400}
    return data


def adm_comment_delete():

    ids = json_to_pyseq(request.argget.all('ids', []))
    pending_delete = int(request.argget.all("pending_delete", 1))

    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)
    if pending_delete:
        r = mdbs["web"].db.comment.update_many(
            {"_id": {"$in": ids}}, {"$set": {"is_delete": 2}})
        if r.modified_count:
            data = {"msg": gettext("Move to a permanently deleted area, {}").format(
                r.modified_count), "msg_type": "s", "custom_status": 204}
        else:
            data = {
                "msg": gettext("Does not match the data to be deleted"),
                "msg_type": "w",
                "custom_status": 400}
    else:
        for tid in ids:
            mdbs["user"].db.user_like.update_many({"type": "comment", "values": str(tid)},
                                              {"$pull": {"values": str(tid)}})
        r = mdbs["web"].db.comment.delete_many(
            {"_id": {"$in": ids}, "is_delete": {"$in": [1, 2]}})
        if r.deleted_count:
            data = {"msg": gettext("Removed from the database, {}").format(
                r.deleted_count), "msg_type": "s", "custom_status": 204}
        else:
            data = {"msg": gettext("No match to relevant data"),
                    "msg_type": "w", "custom_status": 400}
    return data


def adm_comment_restore():

    ids = json_to_pyseq(request.argget.all('ids', []))
    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)
    r = mdbs["web"].db.comment.update_many({"_id": {"$in": ids},
                                        "is_delete": {"$in": [1, 2]}},
                                       {"$set": {"is_delete": 0}})
    if r.modified_count:
        data = {"msg": gettext("Restore success, {}").format(r.modified_count),
                "msg_type": "s", "custom_status": 201}
    else:
        data = {
            "msg": gettext("No match to relevant data"),
            "msg_type": "w",
            "custom_status": 400}

    return data
