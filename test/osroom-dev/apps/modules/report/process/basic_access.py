#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import time
from apps.app import mdbs, cache
from apps.core.utils.get_config import get_config


@cache.cached(key_base64=False, db_type="mongodb")
def get_post_access():
    """
    获取文章基本数据统计
    :return:
    """
    data = {}
    now_time = time.time()
    s_time = (now_time - 86400 * 6) - now_time % 86400
    data["total"] = mdbs["web"].db.post.find({}).count(True)
    data["7_total"] = mdbs["web"].db.post.find(
        {"issue_time": {"$gte": s_time}}).count(True)
    s_time = (now_time - 86400 * 29) - now_time % 86400
    data["30_total"] = mdbs["web"].db.post.find(
        {"issue_time": {"$gte": s_time}}).count(True)

    data["unaudited"] = mdbs["web"].db.post.find(
        {
            "audited": 0,
            'is_delete': 0,
            'issued': 1,
            "audit_score": {
                "$gte": get_config(
                    "content_inspection",
                    "ALLEGED_ILLEGAL_SCORE")}}).count(True)
    # data["draft"] = mdbs["web"].db.post.find({"issued": 0, 'is_delete':0}).count(True)
    # data["unqualified"] = mdbs["web"].db.post.find({"issued": 1, 'is_delete': 0, 'audited':1,
    #                                             'audit_score':{"$lt":get_config("content_inspection",
    #                                                                             "LOWEST_SCORE")}}).count(True)

    return data


@cache.cached(key_base64=False, db_type="mongodb")
def get_comment_access():
    """
    获取评论基本数据统计
    :return:
    """
    data = {}
    now_time = time.time()
    s_time = (now_time - 86400 * 6) - now_time % 86400
    data["total"] = mdbs["web"].db.comment.find({}).count(True)
    data["7_total"] = mdbs["web"].db.comment.find(
        {"issue_time": {"$gte": s_time}}).count(True)
    s_time = (now_time - 86400 * 29) - now_time % 86400
    data["30_total"] = mdbs["web"].db.comment.find(
        {"issue_time": {"$gte": s_time}}).count(True)

    data["unaudited"] = mdbs["web"].db.comment.find(
        {
            "audited": 0,
            'is_delete': 0,
            'issued': 1,
            "audit_score": {
                "$gte": get_config(
                    "content_inspection",
                    "ALLEGED_ILLEGAL_SCORE")}}).count(True)
    # data["unqualified"] = mdbs["web"].db.comment.find({"issued": 1, 'is_delete': 0, 'audited': 1,
    #                                             'audit_score': {"$lt": get_config("content_inspection",
    #                                                                               "LOWEST_SCORE")}}).count(True)

    return data


@cache.cached(key_base64=False, db_type="mongodb")
def get_user_access():
    """
    获取用户基本统计数据
    :return:
    """
    data = {}
    data["total"] = mdbs["user"].db.user.find({}).count(True)
    now_time = time.time()
    s_time = (now_time - 86400 * 6) - now_time % 86400
    data["7_total"] = mdbs["user"].db.user.find(
        {"create_at": {"$gte": s_time}}).count(True)
    s_time = (now_time - 86400 * 29) - now_time % 86400
    data["30_total"] = mdbs["user"].db.user.find(
        {"create_at": {"$gte": s_time}}).count(True)

    return data


@cache.cached(key_base64=False, db_type="mongodb")
def get_message():
    """
    获取系统消息数据
    :return:
    """

    data = {}

    data["email_abnormal"] = mdbs["sys"].db.sys_message.find(
        {"status": "abnormal", "type": "email"}).count(True)
    data["email_error"] = mdbs["sys"].db.sys_message.find(
        {"status": "error", "type": "email"}).count(True)

    data["sms_error"] = mdbs["sys"].db.sys_message.find(
        {"status": "error", "type": "sms"}).count(True)
    data["sms_abnormal"] = mdbs["sys"].db.sys_message.find(
        {"status": "abnormal", "type": "sms"}).count(True)

    return data


@cache.cached(key_base64=False, db_type="mongodb")
def get_plugin():
    """
    获取插件数据
    :return:
    """

    data = {}

    data["plugin_error"] = mdbs["sys"].db.plugin.find(
        {"error": {"$nin": ["", 0, False, None]}}).count(True)
    data["plugin_active"] = mdbs["sys"].db.plugin.find(
        {"active": {"$in": [1, True]}}).count(True)
    data["plugin_total"] = mdbs["sys"].db.plugin.find({}).count(True)

    return data


@cache.cached(key_base64=False, db_type="mongodb")
def get_media():
    """
    获取多媒体数据
    :return:
    """

    data = {}

    data["media_image"] = mdbs["web"].db.media.find({"type": "image"}).count(True)
    data["media_text"] = mdbs["web"].db.media.find({"type": "text"}).count(True)
    data["media_video"] = mdbs["web"].db.media.find({"type": "video"}).count(True)
    data["media_audio"] = mdbs["web"].db.media.find({"type": "audio"}).count(True)
    data["media_other"] = mdbs["web"].db.media.find({"type": "other"}).count(True)

    now_time = time.time()
    s_time = (now_time - 86400 * 6) - now_time % 86400
    data["7_total"] = mdbs["web"].db.media.find(
        {"time": {"$gte": s_time}}).count(True)
    s_time = (now_time - 86400 * 29) - now_time % 86400
    data["30_total"] = mdbs["web"].db.media.find(
        {"time": {"$gte": s_time}}).count(True)

    return data


@cache.cached(key_base64=False, db_type="mongodb")
def get_inform_data():
    """
    获取举报数据
    :return:
    """

    data = {}
    now_time = time.time()
    s_time = (now_time - 86400 * 6) - now_time % 86400
    data["7_post"] = mdbs["web"].db.post.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["7_comment"] = mdbs["web"].db.comment.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["7_user"] = mdbs["user"].db.user.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["7_media"] = mdbs["web"].db.media.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)

    s_time = now_time - now_time % 86400
    data["1_post"] = mdbs["web"].db.post.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["1_comment"] = mdbs["web"].db.comment.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["1_user"] = mdbs["user"].db.user.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["1_media"] = mdbs["web"].db.media.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)

    s_time = now_time - 3600 * 8
    data["8h_post"] = mdbs["web"].db.post.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["8h_comment"] = mdbs["web"].db.comment.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["8h_user"] = mdbs["user"].db.user.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["8h_media"] = mdbs["web"].db.media.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)

    s_time = now_time - 3600 * 3
    data["3h_post"] = mdbs["web"].db.post.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["3h_comment"] = mdbs["web"].db.comment.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["3h_user"] = mdbs["user"].db.user.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)
    data["3h_media"] = mdbs["web"].db.media.find(
        {"inform.update_time": {"$gte": s_time}}).count(True)

    return data
