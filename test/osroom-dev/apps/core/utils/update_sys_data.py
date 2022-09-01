#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import json
import os
import shutil
import time
from collections import OrderedDict
from copy import deepcopy

from apps.app import cache
from apps.configs.sys_config import APPS_PATH, SUPER_PER, \
    GET_DEFAULT_SYS_PER_CACHE_KEY, GET_ALL_PERS_CACHE_KEY
from apps.core.logger.web_logging import web_start_log
from init_datas import INIT_DATAS


def update_mdb_collections(mdbs):
    """
    更新数据库mongodb collection, 不存在的colletion则创建
    :param mdbs:
    :return:
    """

    # 读取配置中的数据库json 数据
    coll_json_file = "{}/configs/mdb_collections.json".format(APPS_PATH)
    if not os.path.exists(coll_json_file):
        return
    with open(coll_json_file) as rf:
        jsondata = rf.read()
        if jsondata:
            collections = json.loads(jsondata)
        else:
            collections = {}

    # 检查数据库collections
    for dbname, colls in collections.items():
        mdb = mdbs[dbname]
        for coll in colls:
            try:
                mdb.dbs.create_collection(coll)
                web_start_log.info(
                    "[DB: {}] Create collection '{}'".format(
                        mdb.name, coll))
            except Exception as e:
                if "already exists" in str(e):
                    web_start_log.info(e)
                else:
                    web_start_log.error(e)


def update_mdbcolls_json_file(mdbs):

    """
    将最新的数据库结构写入配置文件, 方便开发者了解结构
    :param mdbs:
    :return:
    """
    print("Update tables to json file...")
    new_collections = OrderedDict({})
    for dbname, mdb in mdbs.items():
        new_collections[dbname] = {}
        collnames = mdb.db.collection_names()
        for collname in collnames:
            if collname == "system.indexes" or collname.startswith("plug_"):
                continue
            new_collections[dbname][collname] = {}
            data = mdb.dbs[collname].find_one({}, {"_id": 0})
            if data:
                for k, v in data.items():
                    new_collections[dbname][collname][k] = str(type(v))
    with open("{}/configs/mdb_collections.json".format(APPS_PATH), "w") as wf:
        collections = json.dumps(new_collections, indent=4, ensure_ascii=False)
        wf.write(collections)
    print("End")


def init_datas(mdbs, init_theme=True):
    """
    初始web化数据
    :return:
    """

    # 复制最新配置文件
    config_sample_path = "{}/configs/config_sample.py".format(APPS_PATH)
    target_path = "{}/configs/config.py".format(APPS_PATH)
    if os.path.exists(config_sample_path):
        print("Copy config file")
        if os.path.exists(target_path):
            os.remove(target_path)
        shutil.copy(config_sample_path, target_path)

    # 初始化其他数据
    for data in INIT_DATAS:
        db = mdbs["sys"]
        if data["db"] == "osr_web":
            db = mdbs["web"]
        elif data["db"] == "osr_user":
            db = mdbs["user"]
        q = {}
        if "condition" in data:
            q = data["condition"]
        if db.dbs[data["coll"]].find_one(q):
            continue
        else:
            print("* [Initialization data] {}".format(data["coll"]))
            db.dbs[data["coll"]].insert_many(data["datas"])

    if init_theme:
        # 初始化主题数据
        init_theme_data(mdbs)


def init_theme_data(mdbs):
    """
    初始化主题数据
    :param mdbs:
    :return:
    """
    theme = mdbs["sys"].dbs["sys_config"].find_one(
        {"project": "theme", "key": "CURRENT_THEME_NAME"}
    )
    if theme:
        theme_name = theme["value"]
    else:
        return True

    if mdbs["sys"].dbs["theme_display_setting"].find_one({"theme_name": theme_name}):
        print(" * [Init theme] No initialization required")
        return True
    init_data = []
    init_file = "{}/themes/{}/init_setting.json".format(APPS_PATH, theme_name)
    if os.path.exists(init_file):
        # 读取数据
        with open(init_file) as rf:
            jsondata = rf.read()
            if jsondata:
                init_data = json.loads(jsondata)

    # 初始化主题数据
    for data in init_data:
        tempdata = deepcopy(data)
        tempdata["theme_name"] = theme_name
        # 查找是否存在分类
        r = mdbs["web"].dbs["theme_category"].find_one({
            "name": tempdata["category"],
            "type": tempdata["type"],
            "theme_name": theme_name,
            "user_id": 0})
        if r:
            tempdata["category_id"] = str(r["_id"])
        else:
            # 不存在则创建
            r = mdbs["web"].dbs["theme_category"].insert_one(
                {"name": tempdata["category"],
                 "type": tempdata["type"],
                 "theme_name": theme_name,
                 "user_id": 0})
            tempdata["category_id"] = str(r.inserted_id)
        fields = ["title", "link", "text", "name", "code", "code_type"]
        for field in fields:
            if field not in tempdata:
                tempdata[field] = ""
        tempdata["time"] = time.time()
        mdbs["sys"].dbs["theme_display_setting"].insert_one(tempdata)


def compatible_processing(mdbs, stage=1):
    """
    兼容上一个版本
    :return:
    """

    if stage == 1:
        # 当前主题设置加上主题名称
        theme = mdbs["sys"].dbs["sys_config"].find_one(
            {"project": "theme", "key": "CURRENT_THEME_NAME"}
        )
        if theme:
            theme_name = theme["value"]
            mdbs["sys"].dbs["theme_display_setting"].update_many(
                {"theme_name": {"$exists": False}},
                {"$set": {"theme_name": theme_name}})

            # 主题设置的数据分类信息转移
            categorys = mdbs["web"].db.category.find(
                {"type": {"$regex": ".+_theme$"}},
                regular_escape=False
            )
            for category in categorys:
                category["type"] = category["type"].replace("_theme", "")
                category["theme_name"] = theme_name
                r = mdbs["web"].db.theme_category.insert_one(category)
                if r.inserted_id:
                    mdbs["web"].db.category.delete_one({"_id": category["_id"]})

            '''
            v2.0之后新功能: 兼容 2.0Beta, v2.0
            '''
            # 判断是第一次部署网站还是升级版本
            its_not_first = mdbs["user"].dbs["permission"].find_one({})
            if its_not_first and not mdbs["sys"].dbs["theme_nav_setting"].find_one({}):
                # 将导航设置迁移到主题导航设置专属模块数据库
                r = mdbs["sys"].dbs["sys_config"].find(
                    {"project": "theme_global_conf", "key": "TOP_NAV"}
                ).sort([("update_time", -1)]).limit(1)
                if r.count(True):
                    for v in r[0]["value"].values():
                        display_name = v["nav"]
                        updata = {
                            "order": 1,
                            "display_name": display_name,
                            "theme_name": theme_name,
                            "language": "zh_CN"
                        }
                        del v["nav"]
                        updata["json_data"] = v
                        mdbs["sys"].dbs["theme_nav_setting"].update_one(
                            {"theme_name": theme_name, "display_name": display_name},
                            {"$set": updata},
                            upsert=True
                        )
    elif stage == 2:
        # 2020/1/23 version v2.2
        # 更新最高权限
        is_updated = False
        pers = mdbs["user"].dbs["permission"].find({})
        cnt = pers.count(True)
        if cnt:
            pers = pers.sort([("value", -1)])
            per = pers[0]
            root = 0b10000000000000000000000000000000000000000000000000000
            if per["value"] < root:
                mdbs["user"].dbs["permission"].update_one(
                    {"_id": per["_id"]},
                    {"$set": {"value": root}}
                )
                is_updated = True
            if cnt > 1:
                per = pers[1]
                admin = 0b1000000000000000000000000000000000000000000000000000
                if per["value"] < admin:
                    mdbs["user"].dbs["permission"].update_one(
                        {"_id": per["_id"]},
                        {"$set": {"value": admin}}
                    )
                    is_updated = True

        # 更新root角色
        roles = mdbs["user"].dbs["role"].find({})
        if roles.count(True):
            role = roles.sort([("permissions", -1)])[0]
            if role["permissions"] < SUPER_PER:
                mdbs["user"].dbs["role"].update_one(
                    {"_id": role["_id"]},
                    {"$set": {"permissions": SUPER_PER}}
                )
                is_updated = True
        if is_updated:
            cache.delete(key=GET_DEFAULT_SYS_PER_CACHE_KEY, db_type="redis")
            cache.delete(key=GET_ALL_PERS_CACHE_KEY, db_type="redis")
            cache.delete_autokey(fun=".*get_one_user.*", db_type="redis", key_regex=True)

        # 用户添加字段 alias [@HiWoo 2020-03-12]
        r = mdbs["user"].dbs["user"].update_many(
            {
                "alias": {"$exists": False}
            },
            {
                "$set": {"alias": ""}
            }
        )
        if r.modified_count:
            cache.delete_autokey(fun=".*get_one_user.*", db_type="redis", key_regex=True)
