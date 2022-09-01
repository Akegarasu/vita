#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from bson import ObjectId

from apps.app import cache, mdbs


@cache.cached(timeout=7200, key_base64=False, db_type="redis")
def get_one_user(user_id=None, username=None, email=None, mphone_num=None):
    """
    获取一个user, 单条件过滤
    :param user_id:
    :return:
    """
    if user_id:
        q = {"_id": ObjectId(user_id)}
    elif username:
        q = {"username": username}
    elif email:
        q = {"email": email}
    elif mphone_num:
        q = {"mphone_num": mphone_num}
    else:
        return {}
    user = mdbs["user"].db.user.find_one(q)
    if user:
        user["_id"] = str(user["_id"])
    return user


def get_one_user_mfilter(username=None, email=None, op=None):
    """
    获取一个user, 多条件过滤
    :return:
    """

    q = {}

    if username:
        if op == "or":
            if "$or" in q:
                q["$or"].append({"username": username})
            else:
                q["$or"] = [{"username": username}]
        else:
            q["username"] = username
    if email:
        if op == "or":
            if "$or" in q:
                q["$or"].append({"email": email})
            else:
                q["$or"] = [{"email": email}]
        else:
            q["email"] = email

    user = mdbs["user"].db.user.find_one(q)

    return user


def insert_one_user(updata):
    """
    插入一条数据
    :param updata:
    :return:
    """

    r = mdbs["user"].db.user.insert_one(updata)

    fun_name = "get_one_user"
    cache.delete_autokey(
        fun=fun_name,
        db_type="redis",
        username=updata["username"])
    cache.delete_autokey(fun=fun_name, db_type="redis", email=updata["email"])
    return r


def update_one_user(user_id, updata):
    """
    更新一个user
    :param user_id:
    :return:
    """

    r = mdbs["user"].db.user.update_one({"_id": ObjectId(user_id)}, updata)

    if r.modified_count:
        user = mdbs["user"].db.user.find_one({"_id": ObjectId(user_id)})
        clean_get_one_user_cache(user=user)
        return r
    else:
        return r


def delete_one_user(user_id):
    """
    delete user
    :param user_id:
    :return:
    """
    user = mdbs["user"].db.user.find_one({"user_id": ObjectId(user_id)})
    r = mdbs["user"].db.user.delete_one({"_id": ObjectId(user_id)})
    if r.deleted_count:
        clean_get_one_user_cache(user=user)
        return r
    else:
        return r


def clean_get_one_user_cache(user_id=None, user=None):
    """
    清理get_one_user的cache
    :param user:
    :return:
    """
    fun_name = "get_one_user"
    if user_id and not user:
        user = mdbs["user"].db.user.find_one({"_id": ObjectId(user_id)})

    if user:
        cache.delete_autokey(
            fun=fun_name,
            db_type="redis",
            user_id=str(
                user["_id"]))
        cache.delete_autokey(
            fun=fun_name,
            db_type="redis",
            username=user["username"])
        cache.delete_autokey(
            fun=fun_name,
            db_type="redis",
            email=user["email"])
