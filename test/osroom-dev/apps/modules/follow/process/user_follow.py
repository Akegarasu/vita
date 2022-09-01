#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user
from apps.app import mdbs
from apps.core.flask.reqparse import arg_verify
from apps.modules.user.process.get_or_update_user import get_one_user, update_one_user
from apps.modules.user.process.user_profile_process import get_user_public_info, delete_user_info_cache
from apps.utils.format.obj_format import json_to_pyseq, str_to_num
from apps.utils.paging.paging import datas_paging


def follow_user():
    """
    关注一个用户
    :return:
    """

    ids = json_to_pyseq(request.argget.all("ids", []))

    s, r = arg_verify(reqargs=[("id", ids)], required=True)
    if not s:
        return r

    cnt = 0
    for tid in ids[:]:

        if tid != current_user.str_id and get_one_user(user_id=str(tid)):
            r = mdbs["user"].db.user_follow.update_one({"user_id": current_user.str_id, "type": "account"},
                                                   {"$addToSet": {"follow": tid}}, upsert=True)
            if r.modified_count or r.upserted_id:
                cnt += 1
                # 更新粉丝统计
                update_one_user(
                    user_id=str(tid), updata={
                        "$inc": {
                            "fans_num": 1}})
            delete_user_info_cache(user_id=tid)

    if cnt:
        # 更新关注统计
        update_one_user(
            user_id=current_user.str_id, updata={
                "$inc": {
                    "follow_user_num": cnt}})
        delete_user_info_cache(user_id=current_user.str_id)
        data = {
            "msg": gettext("Followed"),
            "msg_type": "s",
            "custom_status": 201}

    elif len(ids) == 1 and ids[0] == current_user.str_id:
        data = {"msg": gettext("You can't follow yourself"),
                "msg_type": "w", "custom_status": 400}
    else:
        data = {"msg": gettext("You are already following this user"),
                "msg_type": "w", "custom_status": 400}

    return data


def unfollow():
    """
    取消关注
    :return:
    """

    ids = json_to_pyseq(request.argget.all("ids", []))

    s, r = arg_verify(reqargs=[("id", ids)], required=True)
    if not s:
        return r

    for tid in ids[:]:
        if mdbs["user"].db.user_follow.find_one(
                {"user_id": current_user.str_id, "type": "account", "follow": tid}):
            # 更新粉丝统计
            update_one_user(user_id=str(tid), updata={"$inc": {"fans_num": -1}})
        else:
            ids.remove(tid)
        delete_user_info_cache(user_id=tid)

    r = mdbs["user"].db.user_follow.update_one(
        {"user_id": current_user.str_id, "type": "account"}, {"$pullAll": {"follow": ids}})

    if r.modified_count:
        # 更新关注统计
        update_one_user(user_id=current_user.str_id,
                        updata={"$inc": {"follow_user_num": -len(ids)}})
        delete_user_info_cache(user_id=current_user.str_id)
        data = {
            "msg": gettext("Unfollow success"),
            "msg_type": "s",
            "custom_status": 201}
    else:
        delete_user_info_cache(user_id=current_user.str_id)
        data = {
            "msg": gettext("Unfollow failed"),
            "msg_type": "w",
            "custom_status": 400}

    return data


def get_followed_users():
    """
    获取一个用户已经关注的用户
    :return:
    """
    user_id = request.argget.all("user_id")
    page = str_to_num(request.argget.all("page", 1))
    pre = str_to_num(request.argget.all("pre", 20))

    s, r = arg_verify(reqargs=[("user　id", user_id)], required=True)
    if not s:
        return r
    data = {"users": []}
    follow_user = mdbs["user"].db.user_follow.find_one({"user_id": user_id, "type": "account"})
    if follow_user:
        data_cnt = len(follow_user["follow"])
        for tid in follow_user["follow"][(page - 1) * pre: page * pre]:
            s, r = get_user_public_info(
                user_id=str(tid),
                is_basic=False,
                determine_following=False,
                current_user_isauth=current_user.is_authenticated
            )
            if s:
                data["users"].append(r)
    else:
        data_cnt = 0
    data["users"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=data["users"])

    return data


def get_fans_users():
    """
    获取用户的粉丝
    :return:
    """
    user_id = request.argget.all("user_id")
    page = str_to_num(request.argget.all("page", 1))
    pre = str_to_num(request.argget.all("pre", 20))
    s, r = arg_verify(reqargs=[("user　id", user_id)], required=True)
    if not s:
        return r
    data = {"users": []}
    fans = mdbs["user"].db.user_follow.find({"type": "account", "follow": user_id})
    data_cnt = fans.count(True)
    for user in fans.skip(pre * (page - 1)).limit(pre):
        s, r = get_user_public_info(user_id=user["user_id"],
                                    is_basic=False,
                                    current_user_isauth=current_user.is_authenticated)
        if s:
            data["users"].append(r)
    data["users"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=data["users"])
    return data
