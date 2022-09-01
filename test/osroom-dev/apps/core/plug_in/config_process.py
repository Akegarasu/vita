#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import time
from apps.app import mdbs, cache, app
from apps.configs.sys_config import PLUG_IN_CONFIG_CACHE_KEY, CONFIG_CACHE_TIMEOUT


def import_plugin_config(plugin_name, config):
    """
    导入插件配置到数据库,已存在的则更新时间
    :param plugin_name 插件名
    :param CONFIG:dict
    :return:
    """
    current_time = time.time()
    for k, v in config.items():
        if "value_type" not in v:
            assert Exception(
                'Plugin configuration import database error, missing "value_type"')

        if "reactivate" not in v:
            v["reactivate"] = True
        if "info" not in v:
            v["info"] = ""

        # 查找相同的配置
        r = mdbs["sys"].db.plugin_config.find_one(
            {
                "plugin_name": plugin_name,
                "key": k,
                "value_type": v["value_type"]
            })
        if not r:
            # 如果不存在
            mdbs["sys"].db.plugin_config.insert_one(
                {
                    "plugin_name": plugin_name,
                    "key": k,
                    "value_type": v["value_type"],
                    "value": v["value"],
                    "reactivate": v["reactivate"],
                    "info": v["info"],
                    "update_time": time.time()
                })
        elif r and r["update_time"] < current_time:
            # 存在, 而且比当前时间前的(防止同时启动多个进程时错乱，导致下面程序当旧数据清理)
            mdbs["sys"].db.plugin_config.update_one(
                {
                    "_id": r["_id"],
                    "update_time": {"$lt": current_time}},
                {
                    "$set": {
                        "update_time": current_time,
                        "reactivate": v["reactivate"],
                        "info": v["info"]}
                    })

    # 删除已不需要的配置
    mdbs["sys"].db.plugin_config.delete_many(
        {"plugin_name": plugin_name, "update_time": {"$lt": current_time}})
    # 更新插件配置缓存, # 删除缓存，达到更新缓存
    cache.delete(key=PLUG_IN_CONFIG_CACHE_KEY)


@cache.cached(timeout=CONFIG_CACHE_TIMEOUT, key=PLUG_IN_CONFIG_CACHE_KEY)
def get_all_config():
    """
    从数据库中查询当前的配置返回
    :return:
    """
    all_configs = mdbs["sys"].db.plugin_config.find({})
    configs = {}
    for config in all_configs:
        configs.setdefault(config["plugin_name"], {})
        configs[config["plugin_name"]][config["key"]] = config["value"]
    return configs


def get_plugin_config(plugin_name, key):
    """
    获取网站动态配置中对应的project中key的值
    :return:
    """
    with app.app_context():
        return get_all_config()[plugin_name][key]


def get_plugin_configs(plugin_name):
    """
    获取网站动态配置中对应的project
    :return:
    """
    with app.app_context():
        return get_all_config()[plugin_name]
