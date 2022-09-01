#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os

import shutil
from flask import request
import regex as re
from flask_babel import gettext

from apps.app import mdbs
from apps.configs.sys_config import THEME_TEMPLATE_FOLDER
from apps.core.flask.reqparse import arg_verify
from apps.core.utils.get_config import get_config


def add_page():

    routing = request.argget.all('routing')
    content = request.argget.all('content', "")
    ctype = request.argget.all('type', 'html')
    theme_name = request.argget.all("theme_name")
    s, r = arg_verify([(gettext("theme name"), theme_name)], required=True)
    if not s:
        return r
    s, r = arg_verify(reqargs=[(gettext("file type"), ctype)], only=["html"],
                      required=True)
    if not s:
        return r
    if ctype == "html":
        dirname = "pages"
    else:
        dirname = "static"

    regex_filter = r"(osr/|osr-admin/)"
    s, r = arg_verify(reqargs=[(gettext("routing"), routing)], required=True)
    if not s:
        data = r
    elif re.search(regex_filter, routing):
        data = {"msg": gettext("This route can not be used"), "msg_type": "w",
                "custom_status": 403}
    else:
        filename = os.path.split(routing)[-1]
        path = "{}/{}/{}/{}".format(
            THEME_TEMPLATE_FOLDER,
            theme_name,
            dirname,
            os.path.split(routing)[0]).replace(
            "//",
            "/")

        # 是否存在同名的目录
        relative_path = "{}/{}".format(path, filename)
        if os.path.exists(relative_path):
            data = {
                "msg": gettext("This route can not be used"),
                "msg_type": "w",
                "custom_status": 403}
            return data

        # 是否存在同名的html文件
        file = "{}/{}.{}".format(path, filename, ctype)
        if os.path.exists(file):
            data = {"msg": gettext("Routing existing"), "msg_type": "w",
                    "custom_status": 403}
            return data

        if not os.path.exists(path):
            os.makedirs(path)
        with open(file, "w") as wf:
            wf.write(content)

        # 记录
        mdbs["sys"].db.theme.update_one({"theme_name": theme_name},
                                    {"$addToSet": {"custom_pages": "{}.{}".format(filename, ctype)}},
                                    upsert=True)

        data = {"msg": gettext("Added successfully"), "msg_type": "s",
                "custom_status": 201, "url": "/{}".format(routing.strip("/"))}
    return data


def delete_page():
    """
    删除再管理端自定义页面
    :return:
    """

    filename = request.argget.all('filename', "index").strip("/")
    file_path = request.argget.all('file_path', "").strip("/")
    theme_name = request.argget.all("theme_name")
    s, r = arg_verify([(gettext("theme name"), theme_name)], required=True)
    if not s:
        return r
    path = os.path.join(
        THEME_TEMPLATE_FOLDER,
        theme_name
    )
    file_path = "{}/{}".format(path, file_path)
    file = os.path.join(file_path, filename)
    if not os.path.exists(file):
        mdbs["sys"].db.theme.update_one(
            {"theme_name": theme_name},
            {"$pull": {"custom_pages": filename}}
        )

        data = {"msg": gettext("File not found,'{}'").format(file),
                "msg_type": "w", "custom_status": 404}
    else:

        custom = mdbs["sys"].db.theme.find_one(
            {
                "theme_name": theme_name,
                "custom_pages": filename
            })
        if custom:
            os.remove(file)
            mdbs["sys"].db.theme.update_one(
                {
                    "theme_name": theme_name
                },
                {"$pull": {"custom_pages": filename}})
            if not os.listdir(file_path):
                shutil.rmtree(file_path)
            data = {"msg": gettext("Successfully deleted"), "msg_type": "s",
                    "custom_status": 204}
        else:
            data = {
                "msg": gettext("This file can not be deleted"),
                "msg_type": "w",
                "custom_status": 403}
    return data
