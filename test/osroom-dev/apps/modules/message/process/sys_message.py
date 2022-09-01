#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os
from bson import ObjectId
from copy import deepcopy
from flask import request
from flask_babel import gettext

from apps.app import mdbs
from apps.utils.format.obj_format import str_to_num, objid_to_str, json_to_pyseq
from apps.utils.paging.paging import datas_paging
from apps.utils.text_parsing.text_parsing import richtext_extract_img
from apps.utils.upload.file_up import file_del


def get_sys_message():
    """
    管理端获取消息
    :return:
    """
    data = {}
    msg_type = request.argget.all("msg_type")
    ctype = request.argget.all("type")
    status = request.argget.all("status", "successful")
    keyword = request.argget.all("keyword", "")
    pre = str_to_num(request.argget.all("pre", 10))
    page = str_to_num(request.argget.all("page", 1))

    if status == "normal":
        status = "successful"
    q = {"status": status, "type": ctype}
    if msg_type:
        q["msg_type"] = msg_type
    if keyword:
        keyword = {"$regex": keyword, "$options": "$i"}
        q["$or"] = [
            {"subject": keyword},
            {"from": keyword},
            {"to": keyword},
            {"body": keyword},
            {"html": keyword},

        ]
    emails = mdbs["sys"].db.sys_message.find(q)
    data_cnt = emails.count(True)
    emails = list(emails.sort(
        [("time", -1)]).skip(pre * (page - 1)).limit(pre))
    data["msgs"] = objid_to_str(emails)
    data["msgs"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=data["msgs"])

    return data


def delete_sys_message():
    """
    删除已发送邮件
    :return:
    """

    ids = json_to_pyseq(request.argget.all("ids", []))
    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)
    q = {"_id": {"$in": ids}}

    # 查找出要删除中的邮件消息
    q2 = deepcopy(q)
    q2["type"] = "email"
    msgs = mdbs["sys"].db.sys_message.find(q2)
    rm_imgs = []  # 要删除的邮件消息图片
    for msg in msgs:
        srcs = richtext_extract_img(richtext=msg["html"])
        rm_imgs.extend(srcs)

    for rm_img in rm_imgs:
        # 获取图片url中唯一部分
        key = os.path.split(rm_img)
        if len(key) > 0:
            key = key[-1]
        else:
            continue
        # 查找出图片对应的key
        img_obj = mdbs["sys"].db.sys_msg_img.find_one(
            {
                "imgs.key": {"$regex": key}
            },
            regular_escape=False
        )
        if img_obj:
            for img in img_obj["imgs"]:
                # 删除
                file_del(img)
            mdbs["sys"].db.sys_msg_img.delete_one({"_id": img_obj["_id"]})

    r = mdbs["sys"].db.sys_message.delete_many(q)
    if r.deleted_count:
        data = {
            "msg": gettext("Successfully deleted"),
            "msg_type": "s",
            "custom_status": 204}
    else:
        data = {
            "msg": gettext("Failed to delete"),
            "msg_type": "w",
            "custom_status": 400}
    return data
