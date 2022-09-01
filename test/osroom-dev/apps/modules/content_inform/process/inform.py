#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import time
from bson import ObjectId
from flask import request
from flask_babel import gettext

from apps.app import mdbs
from apps.core.flask.reqparse import arg_verify
from apps.modules.user.process.get_or_update_user import update_one_user


def content_inform():
    """
    内容举报
    :return:
    """

    ctype = request.argget.all('ctype')
    cid = request.argget.all('cid')
    category = request.argget.all('category')
    details = request.argget.all('details')

    s, r = arg_verify(reqargs=[("cid(content id)", cid)], required=True)
    if not s:
        return r

    s, r = arg_verify(reqargs=[("ctype(content type)", ctype)],
                      required=True, only=["user", "post", "comment", "media"])
    if not s:
        return r

    s, r = arg_verify(
        reqargs=[
            ("category", category)], only=[
            "ad", "junk_info", "plagiarize", "other"], required=True)
    if not s:
        return r

    if category == "other":
        s, r = arg_verify(
            reqargs=[
                (gettext("details"), details)], required=True)
        if not s:
            return r

    up_data = {
        "$inc": {"inform.{}.cnt".format(category): 1, "inform.total": 1},
        "$set": {"inform.update_time": time.time()}
    }

    if details:
        up_data["$addToSet"] = {"inform.{}.details".format(category): details}
    if ctype == "post":
        r = mdbs["web"].db.post.update_one({"_id": ObjectId(cid)}, up_data)
    elif ctype == "comment":
        r = mdbs["web"].db.comment.update_one({"_id": ObjectId(cid)}, up_data)

    elif ctype == "user":
        r = update_one_user(user_id=cid, updata=up_data)

    elif ctype == "media":
        r = mdbs["web"].db.media.update_one({"_id": ObjectId(cid)}, up_data)

    if r.modified_count:
        data = {
            'msg': gettext("Submitted successfully, thanks for your participation"),
            'msg_type': "s",
            "custom_status": 201}
    else:
        data = {'msg': gettext("Submit failed, please try again"),
                'msg_type': "w", "custom_status": 201}
    return data
