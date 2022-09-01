#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import json
from bson import ObjectId
from flask import request, g
from flask_babel import gettext
from flask_login import current_user
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import objid_to_str, json_to_pyseq
from apps.utils.validation.str_format import short_str_verifi
from apps.app import mdbs
from apps.core.utils.get_config import get_config


def get_category_info():
    """
    获取category信息
    :return:
    """
    tid = request.argget.all('id')
    s, r = arg_verify([(gettext("category id"), tid)], required=True)
    if not s:
        return r
    data = {}
    category = mdbs["web"].db.theme_category.find_one({"_id": ObjectId(tid)})
    category["_id"] = str(category["_id"])
    data["category"] = category
    # theme_name = get_config("theme", "CURRENT_THEME_NAME")
    theme_name = g.get_config("theme", "CURRENT_THEME_NAME")
    data["theme_name"] = theme_name
    return data


def get_category_type():

    return {"types": get_config("category", "CATEGORY_TYPE")}


def categorys(user_id=None):

    if user_id is None:
        user_id = current_user.str_id
    data = {}
    ntype = request.argget.all('type')
    theme_name = request.argget.all(
        'theme_name',
        # get_config("theme", "CURRENT_THEME_NAME")
        g.get_config("theme", "CURRENT_THEME_NAME")
    )

    s, r = arg_verify([(gettext("category type"), ntype)], required=True)
    if not s:
        return r
    category = list(mdbs["web"].db.theme_category.find(
        {
            "user_id": user_id,
            "type": ntype,
            "theme_name": theme_name}
    ))
    data["categorys"] = objid_to_str(category, ["_id", "user_id"])
    data["theme_name"] = theme_name
    return data


def category_add(user_id=None):

    if user_id is None:
        user_id = current_user.str_id

    ntype = request.argget.all('type')
    name = request.argget.all('name', '')
    theme_name = request.argget.all('theme_name')

    s, r = arg_verify([(gettext("Theme name"), theme_name)], required=True)
    if not s:
        return r

    s, r = arg_verify([(gettext("category type"), ntype)],
                      only=get_config("category", "CATEGORY_TYPE").values())
    if not s:
        return r
    s1, v = short_str_verifi(name, "class_name")
    s2, r2 = arg_verify(
        reqargs=[
            (gettext("name"), name), ], required=True, max_len=int(
            get_config(
                "category", "CATEGORY_MAX_LEN")))
    if not s1:
        data = {"msg": v, "msg_type": "w", "custom_status": 422}
    elif not s2:
        data = r2
    elif mdbs["web"].db.theme_category.find_one(
        {
            "type": ntype,
            "user_id": user_id,
            "theme_name": theme_name,
            "name": name
        }
        ):
        data = {
            "msg": gettext("Name already exists"),
            "msg_type": "w",
            "custom_status": 403}
    else:
        mdbs["web"].db.theme_category.insert_one(
            {"type": ntype,
             "theme_name": theme_name,
             "user_id": user_id,
             "name": name})
        data = {
            "msg": gettext("Add a success"),
            "msg_type": "s",
            "custom_status": 201}
    data["theme_name"] = theme_name
    return data


def category_edit(user_id=None):

    if user_id is None:
        user_id = current_user.str_id
    tid = request.argget.all('id')
    ntype = request.argget.all('type')
    name = request.argget.all('name')
    # theme_name = get_config("theme", "CURRENT_THEME_NAME")
    theme_name = g.get_config("theme", "CURRENT_THEME_NAME")
    s1, v = short_str_verifi(name, "class_name")
    s2, r2 = arg_verify(
        reqargs=[
            (gettext("name"), name), ], required=True, max_len=int(
            get_config(
                "category", "CATEGORY_MAX_LEN")))
    if not s1:
        data = {"msg": v, "msg_type": "w", "custom_status": 422}
    elif not s2:
        data = r2
    elif mdbs["web"].db.theme_category.find_one(
        {
            "_id": {
                "$ne": ObjectId(tid)
            },
            "type": ntype,
            "user_id": user_id,
            "theme_name": theme_name,
            "name": name
        }
        ):
        data = {
            "msg": gettext("Name already exists"),
            "msg_type": "w",
            "custom_status": 403}
    else:
        r = mdbs["web"].db.theme_category.update_one(
            {"_id": ObjectId(tid), "user_id": user_id}, {"$set": {"name": name}})
        if r.modified_count:
            update_media_category_name.apply_async(
                kwargs={
                    "category_id": tid,
                    "new_name": name
                }
            )
            data = {
                "msg": gettext("Modify the success"),
                "msg_type": "s",
                "custom_status": 201}
        else:
            data = {
                "msg": gettext("No modification"),
                "msg_type": "w",
                "custom_status": 400}
    data["theme_name"] = theme_name
    return data


def update_media_category_name(category_id, new_name):
    """
    更新主题中多媒体category的名称
    """
    mdbs["sys"].db.theme_display_setting.update_many(
        {"category_id": category_id},
        {"$set": {"category": new_name}})


def category_delete(user_id=None):

    if user_id is None:
        user_id = current_user.str_id
    ids = json_to_pyseq(request.argget.all('ids', []))
    if not isinstance(ids, list):
        ids = json.loads(ids)

    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)
    r = mdbs["web"].db.theme_category.delete_many({"_id": {"$in": ids}, "user_id": user_id})
    if r.deleted_count > 0:
        data = {"msg": gettext("Delete the success,{}").format(
            r.deleted_count), "msg_type": "s", "custom_status": 204}
    else:
        data = {
            "msg": gettext("Delete failed"),
            "msg_type": "w",
            "custom_status": 400}
    # theme_name = get_config("theme", "CURRENT_THEME_NAME")
    theme_name = g.get_config("theme", "CURRENT_THEME_NAME")
    data["theme_name"] = theme_name
    return data
