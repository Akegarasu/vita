#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import json
import re

import time
import os
from celery_once import QueueOnce
from flask import request
from flask_babel import gettext
from apps.app import mdbs, celery
from apps.configs.sys_config import PLUG_IN_CONFIG_CACHE_KEY, PLUG_IN_FOLDER
from apps.core.flask.reqparse import arg_verify
from apps.core.plug_in.manager import plugin_manager
from apps.core.utils.get_config import get_config
from apps.utils.pyssh.pyssh import audit_host_info, MySSH


def get_plugin_setting():
    """
    获取插件设置
    :return:
    """

    plugin_name = request.argget.all('plugin_name')
    s, r = arg_verify(reqargs=[("plugin name", plugin_name)], required=True)
    if not s:
        return r
    data = {"configs": []}
    configs = mdbs["sys"].db.plugin_config.find({"plugin_name": plugin_name})
    if configs.count(True):
        configs = list(configs)
        key_hiding = get_config("system", "KEY_HIDING")
        password_exists = False
        for conf in configs:
            conf["_id"] = str(conf["_id"])
            if key_hiding and conf["value_type"] == "password":
                conf["value"] = "Has been hidden"
                password_exists = True

        if key_hiding and password_exists:
            data["msg_type"] = "w"
            data["msg"] = gettext(
                "The KEY_HIDING switch in the system configuration has been enabled."
                " The value of the password type has been replaced.")

        data["configs"] = configs

    plugin = mdbs["sys"].db.plugin.find_one(
        {"plugin_name": plugin_name}, {"_id": 0})
    if plugin:
        data["plugin_info"] = plugin
    else:
        data["plugin_info"] = None

    return data


def update_plugin_setting():
    """
    获取插件设置
    :return:
    """

    plugin_name = request.argget.all('plugin_name')
    key = request.argget.all('key')
    value = request.argget.all('value')
    s, r = arg_verify(
        reqargs=[
            ("plugin name", plugin_name), ("key", key)], required=True)
    if not s:
        return r

    old_conf = mdbs["sys"].db.plugin_config.find_one(
        {"key": key, "plugin_name": plugin_name})
    if not old_conf:
        data = {
            "msg": gettext("There is no such data"),
            "msg_type": "e",
            "custom_status": 404}
    else:
        try:
            if old_conf["value_type"] == "int" or old_conf["value_type"] == "binary":
                value = int(value)
            elif old_conf["value_type"] == "float":
                value = float(value)
            elif old_conf["value_type"] == "string":
                value = str(value)
            elif old_conf["value_type"] == "bool":
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

            elif old_conf["value_type"] == "list":
                # 如果不是list类型,则转为list类型
                if not isinstance(value, list):
                    #  "[]"转list
                    value = json.loads(value)
                if not isinstance(value, list):
                    # "aaa,bbb,ccc"转["aaa", "bbb", "ccc"]
                    value = value.strip(",").split(",")
                    value = [v.strip("\n") for v in value]

            elif old_conf["value_type"] == "dict":
                if not isinstance(value, dict):
                    value = json.loads(value)
                if not isinstance(value, dict):
                    data = {
                        "msg": gettext('The format of the "value" errors, need a "{}" type').format(
                            old_conf["value_type"]),
                        "msg_type": "e",
                        "custom_status": 400}
                    return data
            elif old_conf["value_type"] == "tuple":
                if not isinstance(value, tuple):
                    value = json.loads(value)
                if not isinstance(value, tuple):
                    data = {
                        "msg": gettext('The format of the "value" errors, need a "{}" type').format(
                            old_conf["value_type"]),
                        "msg_type": "e",
                        "custom_status": 400}
                    return data
            elif old_conf["value_type"] == "password":
                value = str(value)
            else:
                data = {
                    "msg": gettext('There is no {}').format(
                        old_conf["value_type"]),
                    "msg_type": "e",
                    "custom_status": 400}
                return data
        except Exception as e:
            data = {
                "msg": gettext('The format of the "value" errors, need a "{}" type').format(
                    old_conf["value_type"]),
                "msg_type": "e",
                "custom_status": 400}
            return data

        conf = {"value": value, "update_time": time.time()}

        # 更新修改数据
        mdbs["sys"].db.plugin_config.update_one(
            {"plugin_name": plugin_name, "key": key},
            {"$set": conf},
            upsert=True)
        # 删除缓存，达到更新缓存
        cache.delete(PLUG_IN_CONFIG_CACHE_KEY)
        data = {
            "msg": gettext("Modify the success"),
            "msg_type": "s",
            "custom_status": 201}
    return data


def refresh_plugin_setting():
    """
    获取插件设置
    :return:
    """

    plugin_name = request.argget.all('plugin_name')
    s, r = arg_verify(reqargs=[("plugin name", plugin_name)], required=True)
    if not s:
        return r

    register_r = plugin_manager.load_plugin(plugin_name, is_import=True)
    if register_r:
        if mdbs["sys"].db.plugin.find_one(
                {"plugin_name": plugin_name, "active": {"$nin": [1, True]}}):
            # 刷新后, 判断如果并位激活的插件,那就注销注册
            plugin_manager.unregister_plugin(plugin_name)
        data = {
            "msg": gettext("Refreshed successfully"),
            "msg_type": "s",
            "custom_status": 201}
    else:
        data = {
            "msg": gettext("Failed to refresh. Please check the previous plug-in page for error messages"),
            "msg_type": "e",
            "custom_status": 400}

    return data


def install_require_package():
    """
    安装插件需要的其他python 包
    :return:
    """

    plugin_name = request.argget.all('plugin_name')
    s, r = arg_verify(reqargs=[("plugin name", plugin_name)], required=True)
    if not s:
        return r
    plugin_req_file_path = "{}/requirements.txt".format(
        os.path.join(PLUG_IN_FOLDER, plugin_name))
    if not os.path.exists(plugin_req_file_path):
        data = {
            "msg": gettext("There is no requirement file"),
            "msg_type": "e",
            "custom_status": 400}
        return data

    with open(plugin_req_file_path) as rf:
        new_reqs = rf.read().split()

    hosts = mdbs["sys"].db.sys_host.find({"host_info.local_ip": {"$exists": True}})
    connection_failed = []
    for host in hosts:
        host_info = host["host_info"]
        s, v = audit_host_info(host_info)
        if not s:
            connection_failed.append(
                {"host_ip": host_info["local_ip"], "error": r})
            continue
        else:
            try:
                ssh = MySSH(host=host_info["local_ip"], port=host_info["port"],
                            username=host_info["username"],
                            password=host_info["password"])
            except BaseException as e:
                connection_failed.append(
                    {"host_ip": host_info["local_ip"], "error": str(e)})
                continue
            if not ssh:
                connection_failed.append(
                    {"host_ip": host_info["local_ip"], "error": "Failed to connect to server host"})
                continue
        ssh.close()
        install_process(plugin_name, host_info, new_reqs)
        install_process.apply_async(
            kwargs={
                "plugin_name": plugin_name,
                "host_info": host_info,
                "packages": new_reqs
            }
        )

    if connection_failed:
        # 更新插件需求包安装状态
        plugin = mdbs["sys"].db.plugin.find_one({"plugin_name": plugin_name}, {
                                            "require_package_install_result": 1})
        for connect in connection_failed:

            if "require_package_install_result" in plugin and plugin[
                    "require_package_install_result"]:
                updated = False
                for old_result in plugin["require_package_install_result"]:
                    if old_result["host_ip"] == connect["host_ip"]:
                        old_result["error"] = connect["error"]
                        old_result["time"] = time.time()
                        updated = True
                        break

                if not updated:
                    result = {
                        "host_ip": connect["host_ip"],
                        "error": connect["error"],
                        "time": time.time()
                    }
                    plugin["require_package_install_result"].append(result)

            else:
                plugin["require_package_install_result"] = [{
                    "host_ip": connect["host_ip"],
                    "error": connect["error"],
                    "time": time.time()}]

        mdbs["sys"].db.plugin.update_one({"plugin_name": plugin_name}, {"$set": {
                                     "require_package_install_result": plugin["require_package_install_result"]}})

        data = {
            "msg": gettext("Some host connections failed. Successfully connected host has installed requirements package in the background"),
            "data": connection_failed,
            "msg_type": "w",
            "custom_status": 201}
    else:
        data = {
            "msg": gettext("Executed related installation commands in the background"),
            "msg_type": "s",
            "custom_status": 201}
    return data


@celery.task(base=QueueOnce, once={'graceful': True})
def install_process(plugin_name, host_info, packages):
    """
    子进程执行安装
    :return:
    """

    ssh = MySSH(host=host_info["local_ip"], port=host_info["port"],
                username=host_info["username"],
                password=host_info["password"])
    if ssh:
        result = []
        venv = ". {}/bin/activate && ".format(
            get_config("py_venv", "VENV_PATH"))
        for package in packages:
            cmd = "{}pip install -U {}".format(venv, package)
            stdin, stdout, stderr = ssh.exec_cmd(cmd)
            for line in stdout.read().decode().split("\n"):
                if re.search(r"\s*Successfully\s+installed.*", line):
                    result.append(line)

        ssh.close()
        packages = " ".join(packages)
        plugin = mdbs["sys"].db.plugin.find_one({"plugin_name": plugin_name}, {
                                            "require_package_install_result": 1})
        if "require_package_install_result" in plugin and plugin["require_package_install_result"]:

            updated = False
            for old_result in plugin["require_package_install_result"]:
                if old_result["host_ip"] == host_info["local_ip"]:
                    old_result["packages"] = packages
                    if result:
                        old_result["result"] = result
                    old_result["time"] = time.time()
                    old_result["error"] = None
                    updated = True
                    break

            if not updated:
                result = {
                    "host_ip": host_info["local_ip"],
                    "packages": packages,
                    "error": None,
                    "time": time.time()
                }
                if result:
                    result["result"] = result

                plugin["require_package_install_result"].append(result)
        else:
            plugin["require_package_install_result"] = [{
                "host_ip": host_info["local_ip"],
                "packages":packages,
                "result":result,
                "error": None,
                "time":time.time()
            }
            ]
        mdbs["sys"].db.plugin.update_one({"plugin_name": plugin_name}, {"$set": {
                                     "require_package_install_result": plugin["require_package_install_result"]}})
