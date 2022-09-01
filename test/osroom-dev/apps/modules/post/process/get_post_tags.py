#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import time

from celery_once import QueueOnce
from flask import request
from apps.app import mdbs, cache, celery
from apps.core.utils.get_config import get_config
from apps.utils.format.obj_format import json_to_pyseq, str_to_num


def get_tags():
    """
    根据条件获取post tags
    :return:
    """
    last_days = str_to_num(request.argget.all('last_days', 360))
    user_id = request.argget.all('user_id')
    tlimit = str_to_num(request.argget.all('limit', 20))
    tsort = json_to_pyseq(request.argget.all('sort', [{"tag_cnt": -1},
                                                      {"like": -1},
                                                      {"comment_num": -1}]))
    # sort
    sort = {}
    for s in tsort:
        sort = dict(sort, **s)

    # 查看是否存在缓存
    cache_key = cache.get_autokey(
        fun="_get_tags",
        key_base64=False,
        db_type="redis",
        user_id=user_id,
        last_days=last_days,
        tlimit=tlimit,
        sort=sort)
    data = cache.get(key=cache_key, db_type="redis")
    if data == cache.cache_none:
        # 调用生成缓存程序生成新缓存
        async_get_tags.apply_async(
            kwargs={
                "user_id": user_id,
                "last_days": last_days,
                "tlimit": tlimit,
                "sort": sort
            }
        )

        # 然后返回最后一次的长期缓存
        data = cache.get(key="LAST_POST_TAGS_CACHE", db_type="mongodb")
    return data


@celery.task(base=QueueOnce, once={'graceful': True})
def async_get_tags(user_id, last_days, tlimit, sort):
    """
    开子进程统计tag结果
    :param last_days:
    :param tlimit:
    :param sort:
    :return:
    """
    _get_tags(user_id=user_id, last_days=last_days, tlimit=tlimit, sort=sort)


@cache.cached(timeout=3600 * 6, key_base64=False, db_type="redis")
def _get_tags(user_id, last_days, tlimit, sort):
    ut = time.time()
    s_time = ut - last_days * 86400 - ut % 86400
    query_conditions = {
        "issue_time": {"$gt": s_time},
        "issued": 1,
        "is_delete": 0,
        "audit_score": {
            "$lt": get_config("content_inspection", "ALLEGED_ILLEGAL_SCORE")}}
    if user_id:
        query_conditions["user_id"] = user_id

    # 查询出部分pv量大的文章
    sort["cnt"] = -1
    r = mdbs["web"].db.post.aggregate([
        {"$match": query_conditions},
        {"$unwind": "$tags"},
        {
            "$group": {"_id": "$tags",
                       "like": {"$sum": "$like"},
                       "comment_num": {"$sum": "$comment_num"}}
        },
        {"$sort": sort},
        {"$limit": tlimit},
    ], allowDiskUse=True)
    data = {"tags": []}
    temp_tags = []
    for result in r:
        tr = {
            "tag": result["_id"],
            "like": result["like"],
            "comment_num": result["comment_num"]
        }
        temp_tags.append(result["_id"])
        data["tags"].append(tr)

    # 计算每个标签实际的文章数量(未过滤时间)
    query_conditions["tags"] = {"$in": temp_tags}
    del query_conditions["issue_time"]
    r = mdbs["web"].db.post.aggregate([
        {"$match": query_conditions},
        {"$unwind": "$tags"},
        {
            "$group": {"_id": "$tags",
                       "tag_cnt": {"$sum": 1}}
        }
    ], allowDiskUse=True)
    temp_tags_cnt = {}
    for result in r:
        temp_tags_cnt[result["_id"]] = result["tag_cnt"]

    for tag in data["tags"]:
        if tag["tag"] in temp_tags_cnt:
            tag["tag_cnt"] = temp_tags_cnt[tag["tag"]]
        else:
            tag["tag_cnt"] = 0

    # sort
    data["tags"] = sorted(data["tags"], key=lambda x: x["tag_cnt"], reverse=True)
    # 保留一份长期缓存
    cache.set(
        key="LAST_POST_TAGS_CACHE",
        value=data,
        ex=3600 * 24 * 7,
        db_type="mongodb")
    return data
