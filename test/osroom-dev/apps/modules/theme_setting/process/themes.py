#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import glob
import json
import os
import time
import zipfile
import shutil
from copy import deepcopy

import yaml
from flask import request
from flask_babel import gettext
from idna import unicode

from apps.app import cache, mdbs
from apps.configs.sys_config import THEME_TEMPLATE_FOLDER, CONFIG_CACHE_KEY, STATIC_PATH,\
    THEME_REQUIRED_CONF
from apps.core.utils.get_config import get_config
from apps.core.utils.update_sys_data import init_theme_data
from apps.utils.format.time_format import time_to_utcdate


def get_theme_names():

    names = []
    for fname in os.listdir(THEME_TEMPLATE_FOLDER):
        path = os.path.join(THEME_TEMPLATE_FOLDER, fname)
        if not os.path.isdir(path):
            continue
        s, r = verify_theme(path, fname, fname)
        if s:
            names.append(fname)
    data = {
        "current_theme_name": get_config(
            "theme",
            "CURRENT_THEME_NAME"
        ),
        "names": names
    }
    return data


def get_theme_readme():
    """
    获取一个主题的文档信息
    :return:
    """

    name = request.argget.all('name')
    path = "{}/{}/readme.md".format(THEME_TEMPLATE_FOLDER, name)
    if os.path.exists(path):
        with open(path) as rf:
            md_text = rf.read()

        data = {
            "msg": gettext("Get success"),
            "msg_type": "s",
            "custom_status": 200,
            "readme": md_text}
    else:
        data = {
            "msg": gettext("Readme file does not exist"),
            "msg_type": "e",
            "custom_status": 400}
    return data


def get_one_theme_info(theme_name):
    """
    获取一个主题信息
    :return:
    """
    path = os.path.join(THEME_TEMPLATE_FOLDER, theme_name)
    if not os.path.isdir(path):
        return False
    s, r = verify_theme(path, theme_name, theme_name)
    new_cover_dir = os.path.join(STATIC_PATH, "media/theme_cover")
    if s:
        fpath = os.path.join(path, "conf.yaml")
        with open(fpath) as rf:
            theme_conf = yaml.safe_load(rf)

            # 每次都拷贝一次, 防止有上传新的主题:主题封面拷贝到apps/static
            if not os.path.exists(new_cover_dir):
                os.makedirs(new_cover_dir)

            cover_path = "{}/{}/{}".format(
                THEME_TEMPLATE_FOLDER,
                theme_conf["theme_name"],
                theme_conf["cover_path"])
            new_cover_path = "{}/{}_{}".format(new_cover_dir,
                                               theme_conf["theme_name"],
                                               os.path.split(theme_conf["cover_path"])[-1])

            if os.path.exists(cover_path):
                cover_path = cover_path.replace("//", "/")
                shutil.copyfile(cover_path, new_cover_path)

            # 检查
            theme_conf["cover_url"] = "/static/media/theme_cover/{}_{}".format(
                theme_conf["theme_name"],
                os.path.split(theme_conf["cover_path"])[-1])
            if theme_conf["theme_name"] == get_config(
                    "theme", "CURRENT_THEME_NAME"):
                theme_conf["current"] = True
            else:
                theme_conf["current"] = False
            return theme_conf
    else:
        return False


def get_themes():
    """
    获取当前已有主题信息
    :return:
    """
    if not os.path.exists(THEME_TEMPLATE_FOLDER):
        os.makedirs(THEME_TEMPLATE_FOLDER)

    data = {"themes": []}
    # 清理主题封面
    new_cover_dir = os.path.join(STATIC_PATH, "media/theme_cover")
    if os.path.exists(new_cover_dir):
        shutil.rmtree(new_cover_dir)

    for fname in os.listdir(THEME_TEMPLATE_FOLDER):
        path = os.path.join(THEME_TEMPLATE_FOLDER, fname)
        if not os.path.isdir(path):
            continue
        s, r = verify_theme(path, fname, fname)
        if s:
            fpath = os.path.join(path, "conf.yaml")
            with open(fpath) as rf:
                theme_conf = yaml.safe_load(rf)

                # 每次都拷贝一次, 防止有上传新的主题:主题封面拷贝到apps/static
                if not os.path.exists(new_cover_dir):
                    os.makedirs(new_cover_dir)

                cover_path = "{}/{}/{}".format(
                    THEME_TEMPLATE_FOLDER,
                    theme_conf["theme_name"],
                    theme_conf["cover_path"])
                new_cover_path = "{}/{}_{}".format(new_cover_dir,
                                                   theme_conf["theme_name"],
                                                   os.path.split(theme_conf["cover_path"])[-1])

                if os.path.exists(cover_path):
                    cover_path = cover_path.replace("//", "/")
                    shutil.copyfile(cover_path, new_cover_path)

                # 检查
                theme_conf["cover_url"] = "/static/media/theme_cover/{}_{}".format(
                    theme_conf["theme_name"],
                    os.path.split(theme_conf["cover_path"])[-1])
                if theme_conf["theme_name"] == get_config(
                        "theme", "CURRENT_THEME_NAME"):
                    theme_conf["current"] = True
                else:
                    theme_conf["current"] = False
                data["themes"].append(theme_conf)
        else:
            data["themes"].append(
                {"theme_name": fname, "current": False, "error": r})

    return data


def upload_theme():
    """
    主题上传
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

    if not os.path.exists(THEME_TEMPLATE_FOLDER):
        os.makedirs(THEME_TEMPLATE_FOLDER)

    fpath = os.path.join(THEME_TEMPLATE_FOLDER, filename)
    if os.path.isdir(fpath) or os.path.exists(fpath):
        data = {"msg": gettext("The same name theme already exists"),
                "msg_type": "w", "custom_status": 403}
        return data

    # 保存主题
    save_file = os.path.join(
        "{}/{}".format(THEME_TEMPLATE_FOLDER, file.filename))
    file.save(save_file)

    # 解压
    with zipfile.ZipFile(save_file) as zfile:
        theme_dirname = zfile.filelist[0].filename.strip("/")
        fpath = os.path.join(THEME_TEMPLATE_FOLDER, theme_dirname)

        if os.path.isdir(fpath) or os.path.exists(fpath):

            data = {"msg": gettext("The same name theme already exists"),
                    "msg_type": "w", "custom_status": 403}
            os.remove(save_file)
            return data

        zfile.extractall(path=THEME_TEMPLATE_FOLDER)

    os.remove(save_file)

    s, r = verify_theme(fpath, theme_dirname, filename)
    if s:
        # 验证通过
        # 主题配置文件
        fpath = os.path.join(fpath, "conf.yaml")
        with open(fpath) as rf:
            theme_conf = yaml.safe_load(rf)
            # 主题封面拷贝到apps/static
            new_cover_dir = os.path.join(STATIC_PATH, "media/theme_cover")
            if not os.path.exists(new_cover_dir):
                os.makedirs(new_cover_dir)

            cover_path = "{}/{}/{}".format(
                THEME_TEMPLATE_FOLDER,
                theme_conf["theme_name"],
                theme_conf["cover_path"])
            new_cover_path = "{}/{}_{}".format(new_cover_dir,
                                               theme_conf["theme_name"],
                                               os.path.split(theme_conf["cover_path"])[-1])

            if os.path.exists(cover_path):
                cover_path = cover_path.replace("//", "/")
                shutil.copyfile(cover_path, new_cover_path)
            data = {
                "msg": gettext("Theme installed successfully"),
                "msg_type": "s",
                "custom_status": 201}
    else:
        # 验证失败
        # 删除上传的文件
        if os.path.exists(os.path.join(THEME_TEMPLATE_FOLDER, filename)):
            shutil.rmtree(os.path.join(THEME_TEMPLATE_FOLDER, filename))
        elif os.path.join(THEME_TEMPLATE_FOLDER, theme_dirname):
            shutil.rmtree(os.path.join(THEME_TEMPLATE_FOLDER, theme_dirname))
        data = {"msg": r, "msg_type": "e", "custom_status": 400}

    return data


def verify_theme(theme_path, theme_dirname, filename):

    # 查看主题是否有配置文件
    fpath = os.path.join(theme_path, "conf.yaml")
    if os.path.exists(fpath) and os.path.isfile(fpath):
        with open(fpath) as rf:
            theme_conf = yaml.safe_load(rf)
            req_conf = THEME_REQUIRED_CONF.copy()
            req_conf = list(set(req_conf).difference(set(theme_conf.keys())))
            if req_conf:
                data = gettext('Configuration file "conf.yaml" but few parameters "{}"').format(
                    ", ".join(req_conf))
                return False, data
            if theme_conf["theme_name"] != filename or theme_conf["theme_name"] != theme_dirname:
                return False, gettext(
                    'The theme name and theme directory name in the configuration are inconsistent.'
                    '("{}" compared with "{}")'.format(
                        theme_conf["theme_name"], theme_dirname))
            return True, None
    else:
        return False, gettext(
            "The theme of the upload is incorrect, the configuration file(conf.yaml) does not exist")


def switch_theme():
    """
    切换主题
    :return:
    """

    theme_name = request.argget.all('theme_name')

    path = os.path.join(THEME_TEMPLATE_FOLDER, theme_name.strip())
    if not os.path.exists(path):
        data = {
            "msg": gettext("Theme does not exist"),
            "msg_type": "e",
            "custom_status": 400}
        return data

    s, r = verify_theme(path, theme_name, theme_name)
    if s:
        # 更新主题数据
        mdbs["sys"].db.sys_config.update_many(
            {"project": "theme", "key": "CURRENT_THEME_NAME"},
            {"$set": {"value": theme_name.strip(), "update_time": time.time()}},
            upsert=True)

        theme_info = get_one_theme_info(theme_name)
        if theme_info and "version" in theme_info:
            mdbs["sys"].db.sys_config.update_many(
                {"project": "theme", "key": "VERSION"},
                {"$set": {"value": theme_info["version"], "update_time": time.time()}},
                upsert=True)

        mdbs["sys"].db.sys_config.update_many(
            {
                "project": "site_config",
                "key": "STATIC_FILE_VERSION"
            },
            {
                "$set": {
                    "value": int(
                        time_to_utcdate(time.time(), "%Y%m%d%H%M%S")),
                    "update_time": time.time()}},
            upsert=True
        )

        cache.delete(CONFIG_CACHE_KEY)
        init_theme_data(mdbs=mdbs)
        data = {
            "msg": gettext("Switch success"),
            "msg_type": "s",
            "custom_status": 201}
    else:
        data = {"msg": r, "msg_type": "e", "custom_status": 400}
    return data


def restore_del_default_settings():

    """
    恢复已删除的默认设置
    :return:
    """

    theme_name = request.argget.all('theme_name')
    path = os.path.join(THEME_TEMPLATE_FOLDER, theme_name.strip())

    init_file = "{}/init_setting.json".format(path)
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

        if not mdbs["sys"].dbs["theme_display_setting"].find_one(
                {"type": tempdata["type"],
                 "name": tempdata["name"],
                 "theme_name": theme_name}):
            fields = ["title", "link", "text", "name", "code", "code_type"]
            for field in fields:
                if field not in tempdata:
                    tempdata[field] = ""
            tempdata["time"] = time.time()
            mdbs["sys"].dbs["theme_display_setting"].insert_one(tempdata)

    data = {
        "msg": gettext("Restored"),
        "msg_type": "s",
        "custom_status": 201}
    return data


def delete_theme():
    """
    删除主题
    :return:
    """

    theme_name = request.argget.all('theme_name')
    path = os.path.join(THEME_TEMPLATE_FOLDER, theme_name.strip())
    if not os.path.exists(path):
        data = {
            "msg": gettext("Theme does not exist"),
            "msg_type": "e",
            "custom_status": 400}
    elif get_config("theme", "CURRENT_THEME_NAME") == theme_name.strip():
        data = {
            "msg": gettext("The current use of the theme can not be deleted"),
            "msg_type": "w",
            "custom_status": 400}
    else:
        # 查看当前已安装主题数量
        num = 0
        for fname in os.listdir(THEME_TEMPLATE_FOLDER):
            path = os.path.join(THEME_TEMPLATE_FOLDER, fname)
            fpath = os.path.join(path, "conf.yaml")
            if os.path.isdir(path) and os.path.exists(fpath):
                num += 1
        if num < 2:
            data = {
                "msg": gettext("Delete failed, at least keep a theme"),
                "msg_type": "w",
                "custom_status": 400}
        else:

            theme_path = os.path.join(THEME_TEMPLATE_FOLDER, theme_name)
            fpath = os.path.join(theme_path, "conf.yaml")
            theme_conf = None
            if os.path.isfile(fpath) and os.path.exists(fpath):
                with open(fpath) as rf:
                    theme_conf = yaml.safe_load(rf)

            shutil.rmtree(theme_path)

            mdbs["sys"].db.theme.delete_many(
                {"theme_name": get_config("theme", "CURRENT_THEME_NAME")})

            # 删除主题封面
            if theme_conf and "theme_name" in theme_conf and "cover_path" in theme_conf:
                cover_dir = os.path.join(STATIC_PATH, "media/theme_cover")
                cover_path = "{}/{}_{}".format(cover_dir,
                                               theme_conf["theme_name"],
                                               os.path.split(theme_conf["cover_path"])[-1])

                if os.path.exists(cover_path):
                    cover_path = cover_path.replace("//", "/")
                    file_split = os.path.splitext(cover_path)
                    os.remove(cover_path)
                    # 删除比例缩放图
                    for f in glob.glob(os.path.join(
                            "{}_w*_h*{}".format(file_split[0], file_split[1]))):
                        os.remove(f)

            data = {
                "msg": gettext("Successfully deleted"),
                "msg_type": "s",
                "custom_status": 204}
    return data
