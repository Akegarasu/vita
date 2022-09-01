#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os
import zipfile
import shutil
from flask import request
from flask_babel import gettext

from apps.app import mdbs, cache
from apps.configs.sys_config import PLUG_IN_FOLDER, PLUG_IN_REQUIRED_CONF, PLUG_IN_CONFIG_CACHE_KEY
from apps.core.flask.reqparse import arg_verify
from apps.core.plug_in.manager import plugin_manager, verify_plugin
from apps.utils.format.obj_format import str_to_num, objid_to_str
from apps.utils.paging.paging import datas_paging


def get_plugins():
    """
    获取插件信息
    :return:
    """
    data = {}
    pre = str_to_num(request.argget.all('pre', 10))
    page = str_to_num(request.argget.all('page', 1))
    keyword = request.argget.all('keyword')
    plugin_manager.load_all_plugin()
    query = {"is_deleted": {"$nin": [1, True]}}
    if keyword:
        keyword = {"$regex": keyword, "$options": "$i"}
        query["$or"] = [
            {"plugin_name": keyword},
            {"alias_name": keyword},
            {"introduce": keyword},
            {"license": keyword},
            {"author": keyword}
        ]
    plugins = mdbs["sys"].db.plugin.find(query)
    data_cnt = plugins.count(True)
    plugins = list(plugins.skip(pre * (page - 1)).limit(pre))
    data["plugins"] = objid_to_str(plugins)
    data["plugins"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=data["plugins"])
    return data


def start_plugin():
    """
    开启一个插件
    :return:
    """

    name = request.argget.all('name')
    s, r = arg_verify(reqargs=[(gettext("name"), name)], required=True)
    if not s:
        return r
    find_query = {"plugin_name": name, "error": {"$in": [0, False]}}
    plugin = mdbs["sys"].db.plugin.find_one(find_query)
    if plugin:
        other_plugin = mdbs["sys"].db.plugin.find_one(
            {"hook_name": plugin["hook_name"], "active": {"$in": [1, True]}})
        if other_plugin:
            data = {
                "msg": gettext(
                    "Plugin[{}] with similar functionality is in use,"
                    " please stop it first").format(
                    other_plugin["plugin_name"]),
                "msg_type": "w",
                "custom_status": 400}
            return data
    r = mdbs["sys"].db.plugin.update_one(find_query, {"$set": {"active": 1}})
    register_r = plugin_manager.register_plugin(name)
    if r.modified_count and register_r:
        # 清除缓存
        r = mdbs["sys"].db.plugin.find_one({"plugin_name": name})
        if r:
            cache.delete_autokey(
                fun="get_plugin_info",
                db_type="redis",
                hook_name=r['hook_name'])

        data = {
            "msg": gettext("Plug-in activated successfully"),
            "msg_type": "s",
            "custom_status": 201}
    elif r.matched_count and register_r:
        data = {
            "msg": gettext("Plug-in is already activated"),
            "msg_type": "w",
            "custom_status": 400}
    else:
        data = {
            "msg": gettext("Plug-in activation failed"),
            "msg_type": "w",
            "custom_status": 400}
    return data


def stop_plugin():
    """
    停用一个插件
    :return:
    """

    name = request.argget.all('name')
    s, r = arg_verify(reqargs=[(gettext("name"), name)], required=True)
    if not s:
        return r
    r = mdbs["sys"].db.plugin.update_one(
        {"plugin_name": name}, {"$set": {"active": 0}})
    if r.matched_count:
        # 清除缓存
        r = mdbs["sys"].db.plugin.find_one({"plugin_name": name})
        if r:
            cache.delete_autokey(
                fun="get_plugin_info",
                db_type="redis",
                hook_name=r['hook_name'])

        data = {
            "msg": gettext("Plug-in stopped successfully"),
            "msg_type": "s",
            "custom_status": 201}
    else:
        data = {
            "msg": gettext("Plug-in failed to stop"),
            "msg_type": "w",
            "custom_status": 400}
    return data


def delete_plugin():
    """
    删除一个插件
    :return:
    """

    name = request.argget.all('name')
    s, r = arg_verify(reqargs=[(gettext("name"), name)], required=True)
    if not s:
        return r

    # 清除缓存
    plug = mdbs["sys"].db.plugin.find_one({"plugin_name": name})

    r = mdbs["sys"].db.plugin.update_one({"plugin_name": name, "active": {"$ne": 1}},
                                     {"$set": {"is_deleted": 1}})
    if r.modified_count or r.matched_count:
        data = {
            "msg": gettext("Successfully deleted"),
            "msg_type": "s",
            "custom_status": 204}
        # 删除配置
        mdbs["sys"].db.plugin_config.delete_many({"plugin_name": name})

        # 删除缓存，达到更新缓存
        cache.delete(PLUG_IN_CONFIG_CACHE_KEY)
        cache.delete_autokey(
            fun="get_plugin_info",
            db_type="redis",
            hook_name=plug['hook_name'])
    else:
        data = {
            "msg": gettext("Failed to delete"),
            "msg_type": "w",
            "custom_status": 400}
    return data


def upload_plugin():
    """
    插件上传
    :return:
    """

    file = request.files["upfile"]
    file_name = os.path.splitext(file.filename)
    filename = os.path.splitext(file.filename)[0]
    extension = file_name[1]
    if not extension.strip(".").lower() in ["zip"]:
        data = {"msg": gettext("File format error, please upload zip archive"),
                "msg_type": "w", "custom_status": 401}
        return data

    if not os.path.exists(PLUG_IN_FOLDER):
        os.makedirs(PLUG_IN_FOLDER)

    fpath = os.path.join(PLUG_IN_FOLDER, filename)
    if os.path.isdir(fpath) or os.path.exists(fpath):
        if mdbs["sys"].db.plugin.find_one(
                {"plugin_name": filename, "is_deleted": {"$in": [0, False]}}):
            # 如果插件没有准备删除标志
            data = {"msg": gettext("The same name plugin already exists"),
                    "msg_type": "w", "custom_status": 403}
            return data
        else:
            # 否则清除旧的插件
            shutil.rmtree(fpath)
            mdbs["sys"].db.plugin.update_one({"plugin_name": filename}, {
                                         "$set": {"is_deleted": 0}})

    # 保存主题
    save_file = os.path.join("{}/{}".format(PLUG_IN_FOLDER, file.filename))
    file.save(save_file)

    # 解压
    with zipfile.ZipFile(save_file) as zfile:
        plugin_dirname = zfile.filelist[0].filename.strip("/")
        fpath = os.path.join(PLUG_IN_FOLDER, plugin_dirname)

        if os.path.isdir(fpath) or os.path.exists(fpath):
            data = {"msg": gettext("The same name theme already exists"),
                    "msg_type": "w", "custom_status": 403}
            os.remove(save_file)
            return data

        zfile.extractall(path=PLUG_IN_FOLDER)

    os.remove(save_file)

    # 查看主题是否有配置文件

    s, r = verify_plugin(fpath)
    if s:
        data = {"msg": r, "msg_type": "s", "custom_status": 201}
    else:
        data = {"msg": r, "msg_type": "e", "custom_status": 400}
    if data["msg_type"] != "s":
        # 删除上传的文件
        if os.path.exists(os.path.join(PLUG_IN_FOLDER, filename)):
            shutil.rmtree(os.path.join(PLUG_IN_FOLDER, filename))
        elif os.path.join(PLUG_IN_FOLDER, plugin_dirname):
            shutil.rmtree(os.path.join(PLUG_IN_FOLDER, plugin_dirname))

    return data
