#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import time
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user
from apps.app import mdbs
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import objid_to_str, str_to_num, json_to_pyseq
from apps.utils.paging.paging import datas_paging


def insert_user_msg(
        user_id,
        ctype,
        content,
        label=None,
        title=None,
        link=None,
        target_id=None,
        target_type=None,
        is_sys_msg=False):
    """
    插入消息
    :param user_id: 可以为数组
    :param ctype:"private_letter", "notice"
    :param title:
    :param content:
    :param link:
    :return:
    """
    s, r = arg_verify(
        reqargs=[
            ("ctype", ctype)], only=[
            "private_letter", "notice"])
    if not s:
        assert Exception("ctype can only be 'private_letter' or 'notice'")
    msg = {
        "type": ctype,
        "label": label,
        "target_id": target_id,
        "target_type": target_type,
        "title": title,
        "content": content,
        "link": link,
        "time": time.time(),
        "is_sys_msg": is_sys_msg
    }
    if isinstance(user_id, list):
        user_id = set([str(uid) for uid in user_id])
        for uid in user_id:
            msg["user_id"] = uid
            mdbs["user"].db.message.insert(msg)
            if "_id" in msg:
                del msg["_id"]
    else:
        msg["user_id"] = str(user_id)
        mdbs["user"].db.message.insert(msg)
    return True


def get_user_msgs(is_admin=None):
    """
    api获取消息
    :return:
    """

    data = {}
    ctype = json_to_pyseq(
        request.argget.all(
            "type", [
                "notice", "private_letter"]))
    label = json_to_pyseq(request.argget.all("label"))
    pre = str_to_num(request.argget.all("pre", 10))
    page = str_to_num(request.argget.all("page", 1))
    status_update = request.argget.all("status_update")

    # admin api才有效的参数
    is_sys_msg = str_to_num(request.argget.all("is_sys_msg", 1))
    keyword = request.argget.all("keyword", "")

    q = {"type": {"$in": ctype}}
    if not is_admin:
        q["user_id"] = current_user.str_id
    else:
        if is_sys_msg:
            q["is_sys_msg"] = True
        else:
            q["is_sys_msg"] = False
        if keyword:
            keyword = {"$regex": keyword}
            q["$or"] = [
                {"title": keyword},
                {"link": keyword},
                {"content": keyword}
            ]
    if label:
        q["label"] = {"$in": label}

    msgs = mdbs["user"].db.message.find(q)
    data_cnt = msgs.count(True)
    msgs = list(msgs.sort([("time", -1)]).skip(pre * (page - 1)).limit(pre))
    ids = [msg["_id"] for msg in msgs]
    data["msgs"] = objid_to_str(msgs)
    data["msgs"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=data["msgs"])

    if not is_admin:
        # user_id为真,表示非管理端获取消息. 标记为已通知
        q = {"user_id": current_user.str_id, "status": {"$ne": "have_read"}}
        data["msgs"]["more"] = get_unread_num(q)
        mdbs["user"].db.message.update_many(q, {"$set": {"status": "notified"}})
        if status_update:
            mdbs["user"].db.message.update_many(
                {"_id": {"$in": ids}}, {"$set": {"status": status_update}})
    return data


def get_unread_num(q):
    """
    获取各类型未读消息个数
    :return:
    """
    r = mdbs["user"].db.message.aggregate([
        {"$match": q},
        {"$group": {"_id": "$label", "total": {"$sum": 1}}},
        {"$project": {"total": "$total"}}
    ],
        allowDiskUse=True,
    )
    data = {}
    for result in r:
        data[result['_id']] = {"unread": result['total']}
    return data

    # map = """
    #     function(){
    #
    #         emit({type:this.type},{total:1});
    #         }
    # """
    # reduce = """
    #     function(key,values){
    #             var ret={total:0};
    #             values.forEach(function(v){
    #                 ret.total += v.total;
    #             });
    #             return ret;
    #         }
    #
    # """


def update_user_msgs():
    """
    api更新消息
    :return:
    """
    ids = json_to_pyseq(request.argget.all("ids", []))
    status_update = request.argget.all("status_update")
    if status_update:
        s, r = arg_verify(
            reqargs=[
                ("status_update", status_update)], only=["have_read"])
        if not s:
            return r
    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)

    # 标记
    r = mdbs["user"].db.message.update_many({"_id": {"$in": ids}},
                                        {"$set": {"status": status_update}})
    if r.modified_count:
        data = {
            'msg': gettext("Update succeed"),
            'msg_type': "s",
            "custom_status": 201}
    else:
        data = {
            'msg': gettext("No changes"),
            'msg_type': "w",
            "custom_status": 201}
    return data


def delete_user_msgs(is_admin=None):
    """
    删除消息
    is_admin:为True 的话, 只能删除系统发出的消息
    :return:
    """

    ids = json_to_pyseq(request.argget.all("ids", []))
    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)
    q = {"_id": {"$in": ids}}
    if not is_admin:
        q["user_id"] = current_user.str_id
    else:
        q["is_sys_msg"] = True

    r = mdbs["user"].db.message.delete_many(q)
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
