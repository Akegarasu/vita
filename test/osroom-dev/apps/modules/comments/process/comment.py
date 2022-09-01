#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from collections import Counter

from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user
import time

from apps.core.flask.reqparse import arg_verify
from apps.modules.comments.process.comment_find import find_comments
from apps.core.utils.get_config import get_config
from apps.modules.message.process.user_message import insert_user_msg
from apps.utils.content_evaluation.content import content_inspection_text
from apps.utils.format.obj_format import json_to_pyseq
from apps.utils.validation.str_format import short_str_verifi, email_format_ver, content_attack_defense
from apps.app import mdbs


def comments():
    target_id = request.argget.all('target_id')
    target_type = request.argget.all('target_type', "post")
    status = request.argget.all('status', "is_issued")
    sort = json_to_pyseq(request.argget.all('sort'))
    page = int(request.argget.all('page', 1))
    pre = get_config("comment", "NUM_PAGE")
    pre = int(request.argget.all('pre', pre))
    basic_query = {'issued': 1, 'is_delete': 0, 'type': target_type, "target_id": target_id,
                   '$or': [{'reply_id': {'$exists': False}}, {'reply_id': {'$in': [None, ""]}}]}
    data = find_comments(
        query_conditions=basic_query,
        page=page,
        pre=pre,
        sort=sort,
        status=status)
    return data


def comment_issue():

    if not get_config("comment", "OPEN_COMMENT"):
        data = {"msg": gettext("Comment feature is not open"),
                "msg_type": "w", "custom_status": 401}
        return data

    target_id = request.argget.all('target_id')  # 目标ID指的是什么事件的评论
    target_type = request.argget.all('target_type', "post")
    content = request.argget.all('content')
    reply_id = request.argget.all('reply_id')  # 回复哪条评论
    reply_user_id = request.argget.all('reply_user_id')  # 回复的评论的用户ID
    reply_username = request.argget.all('reply_username')  # 回复的评论的用户名

    s, r = arg_verify(
        reqargs=[
            (gettext("comment"), content)], min_len=1, max_len=int(
            get_config(
                "comment", "MAX_LEN")))
    if not s:
        return r
    s, r = arg_verify(
        reqargs=[
            ("target_id", target_id), ("target_type", target_type)], required=True)
    if not s:
        return r

    if reply_id:
        s, r = arg_verify(
            reqargs=[
                ("reply_user_id", reply_user_id), ("reply_username", reply_username)], required=True)
        if not s:
            return r

    """
    查看最后一次评论时间
    """
    tquery = {"issue_time": {"$gt": time.time() -
                             int(get_config("comment", "INTERVAL"))}}
    if current_user.is_authenticated:
        user_id = current_user.str_id
        username = current_user.username
        email = None
        tquery["user_id"] = user_id

    elif get_config("comment", "TRAVELER_COMMENT"):
        user_id = None
        username = request.argget.all('username')
        email = request.argget.all('email')
        # 用户名格式验证
        r, s = short_str_verifi(username)
        if not r:
            data = {'msg': s, 'msg_type': "e", "custom_status": 422}
            return data

        # 邮箱格式验证
        r, s = email_format_ver(email)
        if not r:
            data = {'msg': s, 'msg_type': "e", "custom_status": 422}
            return data
        tquery["email"] = email

    else:
        data = {
            "msg": gettext("Guest reviews feature is not open, please login account comments"),
            "msg_type": "w",
            "custom_status": 401}
        return data

    if mdbs["web"].db.comment.find(tquery).count(
            True) >= int(get_config("comment", "NUM_OF_INTERVAL")):
        # 频繁评论
        data = {"msg": gettext("You comment too often and come back later"),
                "msg_type": "e", "custom_status": 400}
        return data

    target = None
    if target_type == "post":
        target = mdbs["web"].db.post.find_one({"_id": ObjectId(target_id),
                                           "issued": {"$in": [1, True]}})
        if not target:
            data = {
                "msg": gettext("Articles do not exist or have not been published"),
                "msg_type": "w",
                "custom_status": 400}
            return data

        target_user_id = str(target["user_id"])
        target_brief_info = target["title"]

    if not target:
        data = {"msg": gettext("Your comment goal does not exist"),
                "msg_type": "w", "custom_status": 400}
        return data

    issue_time = time.time()
    # 自动审核内容
    r = content_inspection_text(content)

    audit_score = r["score"]
    audit_label = r["label"]
    if r["label"] == "detection_off" or (
            "suggestion" in r and r["suggestion"] == "review"):
        # 未开启审核或无法自动鉴别,　等待人工审核
        audited = 0
        audit_way = "artificial"
    elif r["label"] == "no_plugin":
        # 没有检查插件
        audited = 0
        audit_way = "artificial"

    else:
        audit_label = r["label"]
        audited = 1
        audit_way = "auto"
        # 加强审核

    cad = content_attack_defense(content)
    content = cad["content"]
    if cad["security"] < 100:
        audit_label = "attack"
        audited = 1
        audit_way = "auto"
        audit_score = 100

    comment = {
        "target_id": str(target_id),
        "target_user_id": target_user_id,
        "target_brief_info": target_brief_info,
        "type": target_type,
        "user_id": user_id,
        "username": username,
        "email": email,
        "content": content,
        "issued": 1,
        "audited": audited,
        "audit_score": audit_score,
        "audit_label": audit_label,
        "audit_way": audit_way,
        "audit_user_id": None,
        "issue_time": issue_time,
        "word_num": len(content),
        "is_delete": 0,
        "like_user_id": [],
        "like": 0
    }

    if reply_id:
        comment["reply_id"] = reply_id
        comment["reply_user_id"] = reply_user_id
        comment["reply_username"] = reply_username

    r = mdbs["web"].db.comment.insert_one(comment)


    # 如果已审核, 并且违规分数高于正常
    if (audited and audit_score >= get_config(
            "content_inspection", "ALLEGED_ILLEGAL_SCORE")) or cad["security"] < 100:
        # 通知评论不通过
        msg_content = {"text": content}
        insert_user_msg(
            user_id=user_id,
            ctype="notice",
            label="audit_failure",
            title=gettext("[Label:{}]Comment on alleged violations").format(audit_label),
            content=msg_content,
            target_id=str(
                r.inserted_id),
            target_type="comment")

    elif audit_score < get_config("content_inspection", "ALLEGED_ILLEGAL_SCORE"):
        # 更新文章中的评论数目
        if target_type == "post":
            mdbs["web"].db.post.update_one({"_id": ObjectId(target_id)}, {
                                       "$inc": {"comment_num": 1}})

        if current_user.is_authenticated:
            # 评论正常才通知被评论用户
            user_ids = [target_user_id]
            if reply_id:
                user_ids.append(reply_user_id)
            user_ids = list(set(user_ids))
            if user_id in user_ids:
                user_ids.remove(user_id)

            msg_content = {
                "id": str(r.inserted_id),
                "reply_id": reply_id,
                "reply_user_id": reply_user_id,
                "reply_username": reply_username,
                "user_id": user_id,
                "username": username,
                "text": content}
            insert_user_msg(
                user_id=user_ids,
                ctype="notice",
                label="comment",
                title=target_brief_info,
                content=msg_content,
                target_id=target_id,
                target_type=target_type)

    if current_user.is_authenticated:
        data = {
            "msg": gettext("Successful reviews"),
            "msg_type": "s",
            "custom_status": 201}
    else:
        data = {
            "msg": gettext("Success back, waiting for the system audit."),
            "msg_type": "s",
            "custom_status": 201}

    return data


def comment_delete():
    ids = json_to_pyseq(request.argget.all('ids', []))
    reply_ids = ids[:]
    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)
    r1 = mdbs["web"].db.comment.update_many({"_id": {"$in": ids},
                                         "user_id": current_user.str_id},
                                         {"$set": {"is_delete": 1}})

    if r1.modified_count:

        r2 = mdbs["web"].db.comment.update_many({"reply_id": {"$in": reply_ids}},
                                            {"$set": {"is_delete": 1}})
        # 更新target 中的评论数
        comments = []
        if r2.modified_count:
            comments = list(mdbs["web"].db.comment.find(
                {"reply_id": {"$in": reply_ids}}, {"target_id": 1, "type": 1}))

        comments.extend(list(mdbs["web"].db.comment.find(
            {"_id": {"$in": ids}}, {"target_id": 1, "type": 1})))
        target_ids = []
        for c in comments:
            target_ids.append((c["target_id"], c["type"]))
        target_ids = dict(Counter(target_ids))
        if comments[0]["type"] == "post" and target_ids:
            for k, v in target_ids.items():
                # 更新文章中的评论数
                if k[1] == "post":
                    mdbs["web"].db.post.update_many(
                        {"_id": ObjectId(k[0])},
                        {
                            "$inc": {"comment_num": -1 * v}
                        })

        data = {
            "msg": gettext("Delete the success"),
            "msg_type": "s",
            "custom_status": 204}
    else:
        data = {
            "msg": gettext("Delete failed"),
            "msg_type": "w",
            "custom_status": 400}
    return data


def comment_like():
    tid = request.argget.all('id')
    like_comment = mdbs["user"].db.user_like.find_one(
        {"user_id": current_user.str_id, "type": "comment"})
    if not like_comment:
        user_like = {
            "values": [],
            "type": "comment",
            "user_id": current_user.str_id
        }
        mdbs["user"].db.user_like.insert_one(user_like)
        r1 = mdbs["user"].db.user_like.update_one(
            {"user_id": current_user.str_id, "type": "comment"}, {"$addToSet": {"values": tid}})
        r2 = mdbs["web"].db.comment.update_one({
            "_id": ObjectId(tid)},
            {"$inc": {"like": 1},
            "$addToSet": {"like_user_id": current_user.str_id}})

    else:
        if tid in like_comment["values"]:
            like_comment["values"].remove(tid)
            r2 = mdbs["web"].db.comment.update_one({"_id": ObjectId(tid)}, {
                                               "$inc": {"like": -1}, "$pull": {"like_user_id": current_user.str_id}})
        else:
            like_comment["values"].append(tid)
            r2 = mdbs["web"].db.comment.update_one({"_id": ObjectId(tid)}, {"$inc": {"like": 1}, "$addToSet": {
                "like_user_id": current_user.str_id}})
        r1 = mdbs["user"].db.user_like.update_one({"user_id": current_user.str_id, "type": "comment"},
                                              {"$set": {"values": like_comment["values"]}})

    if r1.modified_count and r2.modified_count:
        data = {"msg": gettext("Success"), "msg_type": "s", "custom_status": 201}
    else:
        data = {"msg": gettext("Failed"), "msg_type": "w", "custom_status": 400}
    return data
