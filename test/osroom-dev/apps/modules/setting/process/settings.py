#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import json
from flask import request
from flask_babel import gettext
import time
from apps.configs.sys_config import CONFIG_CACHE_KEY
from apps.core.flask.reqparse import arg_verify
from apps.core.utils.get_config import get_config
from apps.utils.format.obj_format import json_to_pyseq, str_to_num
from apps.utils.format.time_format import time_to_utcdate
from apps.app import cache, mdbs
from apps.utils.paging.paging import datas_paging


def sys_config_version():

    version_uses = mdbs["sys"].db.sys_config.find_one(
        {"new_version": {"$exists": True}}, {"_id": 0})
    hosts = list(mdbs["sys"].db.sys_host.find({"type": "web"}))
    key_hiding = get_config("system", "KEY_HIDING")
    for h in hosts:
        h["_id"] = str(h["_id"])
        if key_hiding and "password" in h["host_info"] and h["host_info"]["password"]:
            h["host_info"]["password"] = "Has been hidden"

    version_uses["used_versions"].reverse()
    data = {"version": version_uses, "hosts": hosts}
    return data


def conf_version_switch():

    switch_version = request.argget.all('switch_version')
    disable_update = request.argget.all('disable_update')
    host_ip = request.argget.all('host_ip')
    version = mdbs["sys"].db.sys_config.find_one(
        {"new_version": {"$exists": True}}, {"_id": 0})
    if switch_version is None or disable_update is None:
        data = {
            "msg": gettext("Lack of parameter"),
            "msg_type": "w",
            "custom_status": 400}

    else:
        if switch_version:
            if switch_version not in version["used_versions"]:
                data = {
                    "msg": "There is no the version history",
                    "msg_type": "w",
                    "custom_status": 400}
            elif not mdbs["sys"].db.sys_config.find_one({"conf_version": switch_version}):
                data = {
                    "msg": "This configuration version data does not exist",
                    "msg_type": "w",
                    "custom_status": 404}
            else:
                host_version = mdbs["sys"].db.sys_host.find_one(
                    {"type": "web", "host_info.local_ip": host_ip})
                if switch_version == host_version["conf_version"]:
                    mdbs["sys"].db.sys_host.update_one({"type": "web", "host_info.local_ip": host_ip},
                                                   {"$set": {"switch_conf_version": None}})
                else:
                    mdbs["sys"].db.sys_host.update_one({"type": "web", "host_info.local_ip": host_ip}, {
                                                   "$set": {"switch_conf_version": switch_version}})
                data = {
                    "msg": gettext("Switch success"),
                    "msg_type": "s",
                    "custom_status": 201}

        if disable_update is not None:
            disable_update = int(disable_update)
            mdbs["sys"].db.sys_host.update_one({"type": "web", "host_info.local_ip": host_ip}, {
                                           "$set": {"disable_update_conf": disable_update}})
            data = {
                "msg": gettext("Switch success"),
                "msg_type": "s",
                "custom_status": 201}

    return data


def get_sys_configs():

    data = {}
    project = json_to_pyseq(request.argget.all('project', []))
    keyword = request.argget.all('keyword', "")
    project_info = str_to_num(request.argget.all('project_info', 0))
    project_info_page = str_to_num(request.argget.all('project_info_page', 1))
    project_info_pre = str_to_num(request.argget.all('project_info_pre', 10))

    new_version = mdbs["sys"].db.sys_config.find_one(
        {"new_version": {"$exists": True}}, {"_id": 0})["new_version"]
    query = {
        "conf_version": new_version,
        "__sort__": {
            "$exists": True,
            "$ne": ""}}

    if project:
        query["project"] = {"$in": project}
    if keyword:
        keyword = {"$regex": keyword, "$options": "$i"}
        query["$or"] = [{"project": keyword},
                        {"key": keyword},
                        {"value": keyword},
                        {"info": keyword}]
    if project_info:
        temp_projects = mdbs["sys"].db.sys_config.find(
            query,
            {
                "project": 1,
                "__info__": 1,
                "__restart__": 1,
                "__sort__": 1,
                "update_time": 1,
                "_id": 0
            }
        )
        data["projects"] = []
        exist_project = []
        for pr in temp_projects:
            if pr["project"] not in exist_project:
                data["projects"].append(pr)
                exist_project.append(pr["project"])

        data_cnt = len(data["projects"])
        data["projects"] = sorted(
            data["projects"],
            key=lambda x: x["__sort__"])
        data["projects"] = data["projects"][(project_info_page - 1) * project_info_pre:(
            project_info_page - 1) * project_info_pre + project_info_pre]
        data["projects"] = datas_paging(
            pre=project_info_pre,
            page_num=project_info_page,
            data_cnt=data_cnt,
            datas=data["projects"])

        return data

    confs = mdbs["sys"].db.sys_config.find(
        query).sort([("__sort__", 1), ("sort", 1)])
    if confs.count(True):
        confs = confs
        temp_list_other = []
        temp_list_json = []

        # 将值是list和dict的配置放发哦数组后面
        key_hiding = get_config("system", "KEY_HIDING")
        password_exists = False
        for conf in confs:
            conf["_id"] = str(conf["_id"])

            if key_hiding and conf["type"] == "password":
                conf["value"] = "Has been hidden"
                password_exists = True
            if conf["type"] in ["list", "dict"]:
                temp_list_json.append(conf)
            else:
                temp_list_other.append(conf)
        temp_list_other.extend(temp_list_json)

        data["configs"] = temp_list_other
        if key_hiding and password_exists:
            data["msg_type"] = "w"
            data["msg"] = gettext(
                "The KEY_HIDING switch in the system configuration has been enabled."
                " The value of the password type has been replaced.")
    else:
        data = {
            "msg": gettext("There is no such data"),
            "msg_type": "warning",
            "custom_status": 400}
    return data


def sys_config_edit():

    key = request.argget.all('key')
    project = request.argget.all('project')
    value = request.argget.all('value')
    info = request.argget.all('info')
    version = mdbs["sys"].db.sys_config.find_one(
        {"new_version": {"$exists": True}}, {"_id": 0})

    s, r = arg_verify(
        reqargs=[
            ("key", key), ("project", project)], required=True)
    if not s:
        return r

    old_conf = mdbs["sys"].db.sys_config.find_one(
        {"key": key, "project": project, "conf_version": version["new_version"]})
    if not old_conf:
        data = {
            "msg": gettext("There is no such data"),
            "msg_type": "e",
            "custom_status": 404}
    else:
        try:
            if old_conf["type"] == "int" or old_conf["type"] == "binary":
                value = int(value)
            elif old_conf["type"] == "float":
                value = float(value)
            elif old_conf["type"] == "string":
                value = str(value)
            elif old_conf["type"] == "bool":
                try:
                    value = int(value)
                    if value:
                        value = True
                    else:
                        value = False
                except BaseException:
                    pass
                if value or (
                    isinstance(
                        value,
                        str) and value.upper() != "FALSE"):
                    value = True
                else:
                    value = False

            elif old_conf["type"] == "list":
                # 如果不是list类型,则转为list类型
                if not isinstance(value, list):
                    #  "[]"转list
                    value = json.loads(value)
                if not isinstance(value, list):
                    # "aaa,bbb,ccc"转["aaa", "bbb", "ccc"]
                    value = value.strip(",").split(",")
                    value = [v.strip("\n") for v in value]

            elif old_conf["type"] == "dict":
                if not isinstance(value, dict):
                    value = json.loads(value)
                if not isinstance(value, dict):
                    data = {
                        "msg": gettext('The format of the "value" errors, need a "{}" type').format(
                            old_conf["type"]), "msg_type": "e", "custom_status": 400}
                    return data
            elif old_conf["type"] == "tuple":
                if not isinstance(value, tuple):
                    value = json.loads(value)
                if not isinstance(value, tuple):
                    data = {
                        "msg": gettext('The format of the "value" errors, need a "{}" type').format(
                            old_conf["type"]), "msg_type": "e", "custom_status": 400}
                    return data
            elif old_conf["type"] == "password":
                value = str(value)
            else:
                data = {
                    "msg": gettext('There is no {}').format(
                        old_conf["type"]),
                    "msg_type": "e",
                    "custom_status": 400}
                return data
        except Exception as e:
            data = {
                "msg": gettext('The format of the "value" errors, need a "{}" type').format(
                    old_conf["type"]),
                "msg_type": "e",
                "custom_status": 400}
            return data
        if not info:
            info = old_conf["info"]
        conf = {"value": value, "update_time": time.time(), "info": info}

        # 更新版本
        # 解释:只要有一台服务器端重启web并更新配置, 则会把重启时最新版本加入到used_version中
        if version["new_version"] in version["used_versions"]:

            # 如果目前的最新版本号在used_version中, 则本次修改就要生成更新的配置版本
            now_version = time_to_utcdate(tformat="%Y_%m_%d_%H_%M_%S")
            old_version = mdbs["sys"].db.sys_config.find({"project": {"$exists": True},
                                                      "conf_version": version["new_version"]},
                                                     {"_id": 0})
            # 生成最新版本配置
            for v in old_version:
                v["conf_version"] = now_version
                mdbs["sys"].db.sys_config.insert_one(v)

            # 更新当前使用的最新版本号
            mdbs["sys"].db.sys_config.update_one({"new_version": {"$exists": True}}, {
                                             "$set": {"new_version": now_version}})

            # 删除多余的配置版本
            ver_cnt = len(version["used_versions"])
            if ver_cnt >= 15:
                rm_vers = version["used_versions"][0:ver_cnt - 15]
                mdbs["sys"].db.sys_config.update_one({"new_version": {"$exists": True}}, {
                                                 "$set": {"used_versions": version["used_versions"][ver_cnt - 15:]}})
                mdbs["sys"].db.sys_config.delete_many(
                    {"version": {"$in": rm_vers}})
        else:
            # 否则, 本次修改暂不生成新配置版本
            now_version = version["new_version"]

        # 更新修改数据
        mdbs["sys"].db.sys_config.update_one(
            {"project": project, "key": key, "conf_version": now_version},
            {"$set": conf}, upsert=True)

        # 删除缓存，达到更新缓存
        cache.delete(CONFIG_CACHE_KEY)
        data = {
            "msg": gettext("Modify the success"),
            "msg_type": "s",
            "custom_status": 201}
    return data
