#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from bson import ObjectId
from flask_babel import gettext
from flask_login import current_user
from apps.utils.upload.get_filepath import get_avatar_url
from apps.app import mdbs, cache


# 查询比较多, 加上缓存
@cache.cached(key_base64=False, db_type="redis")
def get_user_public_info(**kwargs):
    """
    获取用户公开信息
    注意, 函数中不要写默认参数，使用kwargs, 方便更新用户数据时清理缓存
    :param user_id:
    :param is_basic: 默认False, 为Ture时只返回最基础的数据
    :param determine_following:判断当前登录用户是否有关注该用户, 前提是is_basic参数为False
    :return:
    """
    user_id = kwargs.get("user_id")
    is_basic = kwargs.get("is_basic", 0)
    determine_following = kwargs.get("determine_following", True)
    user = mdbs["user"].db.user.find_one(
        {
            "_id": ObjectId(user_id)},
                                     {
                                         "username": 1,
                                         "custom_domain": 1,
                                         "homepage":1,
                                         "avatar_url": 1,
                                         "introduction": 1,
                                         "gender": 1
                                     })
    if not user:
        return False, gettext("The specified user is not found")
    else:
        user["_id"] = str(user["_id"])
        if "homepage" not in user:
            user["homepage"] = ""
        user["custom_domain"] = str(user["custom_domain"])
        user["avatar_url"]["url"] = get_avatar_url(user["avatar_url"])
        if not is_basic:
            user["follow"] = get_user_follow_data(
                user["_id"], determine_following=determine_following)
        return True, user


# 查询比较多, 加上缓存
@cache.cached(key_base64=False, db_type="redis")
def get_user_all_info(**kwargs):
    """
    获取用户全部信息, 密码除外
    注意, 函数中不要写默认参数，使用kwargs, 方便更新用户数据时清理缓存
    :param user_id:
    :param is_basic: 默认False, 为Ture时只返回最基础的数据
    :param determine_following:判断当前登录用户是否有关注该用户, 前提是is_basic参数为False
    :return:
    """

    user_id = kwargs.get("user_id")
    is_basic = kwargs.get("is_basic", 0)
    determine_following = kwargs.get("determine_following", True)

    user = mdbs["user"].db.user.find_one(
        {"_id": ObjectId(user_id)}, {"password": 0})
    if not user:
        return False, gettext("The specified user is not found")
    else:
        user["_id"] = str(user["_id"])
        user["avatar_url"]["url"] = get_avatar_url(user["avatar_url"])
        if not is_basic:
            user["follow"] = get_user_follow_data(
                user["_id"], determine_following=determine_following)
            # 登录日志
            user["user_login_log"] = []
            user_login_log = mdbs["user"].db.user_login_log.find_one(
                {"user_id": user["_id"]}, {"user_id": 0})
            user["user_login_log"] = []
            if user_login_log:
                user_login_log["_id"] = str(user_login_log["_id"])
                user["user_login_log"] = user_login_log
        return True, user


def get_user_follow_data(user_id, determine_following=True):
    """
    获取用户关注数据
    :param user_id:
    :param determine_following:判断当前登录用户是否有关注该用户
    :return:
    """
    follow = {"fans_num": mdbs["user"].db.user_follow.find(
        {"follow": user_id}).count(True)}
    user_follow = mdbs["user"].db.user_follow.find_one({"user_id": user_id})
    if user_follow:
        follow["follow_user_num"] = len(user_follow["follow"])
    else:
        follow["follow_user_num"] = 0
    if determine_following:
        if current_user.is_authenticated and mdbs["user"].db.user_follow.find_one(
                {"user_id": current_user.str_id, "follow": user_id}):
            follow["current_following"] = True
        else:
            follow["current_following"] = False
    else:
        follow["current_following"] = False
    return follow


def delete_user_info_cache(user_id):
    """
    清理user缓存
    :param user_id:
    :return:
    """
    # 清理user信息数据缓存
    cache.delete_autokey(
        fun="get_user_public_info",
        user_id=user_id,
        db_type="redis",
        key_regex=True)
    cache.delete_autokey(
        fun="get_user_all_info",
        user_id=user_id,
        db_type="redis",
        key_regex=True)
