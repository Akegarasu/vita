#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os
from flask import request
from flask_babel import gettext
from apps.app import mdbs
from apps.configs.sys_config import THEME_TEMPLATE_FOLDER
from apps.core.flask.reqparse import arg_verify
from apps.core.utils.get_config import get_config
from apps.utils.file_process.dir_file import file_traversal
from apps.utils.paging.paging import datas_paging


def get_static_files():

    page = int(request.argget.all('page', 1))
    pre = int(request.argget.all('pre', 15))
    keyword = request.argget.all('keyword', "")
    ntype = request.argget.all('type', "all")
    theme_name = request.argget.all("theme_name")

    s, r = arg_verify([(gettext("theme name"), theme_name)], required=True)
    if not s:
        return r
    regex_filter = r".+\.(html|js|css)$"
    path = os.path.join(
        THEME_TEMPLATE_FOLDER, theme_name)
    temp_files = file_traversal(path, regex_filter=regex_filter)

    if ntype == "custom":
        theme_custom = mdbs["sys"].db.theme.find_one(
            {"theme_name": theme_name})
        if not theme_custom or not theme_custom["custom_pages"]:
            theme_custom = False
    else:
        theme_custom = False

    if ntype != "custom":
        if theme_custom:
            for file in temp_files[:]:
                if file["name"] in theme_custom["custom_pages"]:
                    temp_files.remove(file)
                else:
                    if keyword:
                        if keyword in file["path"] or keyword in file["name"]:
                            file["is_custom_page"] = False
                            file["relative_path"] = file["path"].replace(
                                path, "").strip("/")
                        else:
                            temp_files.remove(file)
                    else:
                        file["is_custom_page"] = False
                        file["relative_path"] = file["path"].replace(
                            path, "").strip("/")
        else:
            for file in temp_files[:]:
                if keyword:
                    if keyword in file["path"] or keyword in file["name"]:
                        file["is_custom_page"] = False
                        file["relative_path"] = file["path"].replace(
                            path, "").strip("/")
                    else:
                        temp_files.remove(file)
                else:
                    file["is_custom_page"] = False
                    file["relative_path"] = file["path"].replace(
                        path, "").strip("/")

    elif ntype == "custom":
        if theme_custom:
            for file in temp_files[:]:
                if file["name"] in theme_custom["custom_pages"]:
                    if keyword:
                        if keyword in file["path"] or keyword in file["name"]:
                            file["is_custom_page"] = True
                            file["relative_path"] = file["path"].replace(
                                path, "").strip("/")
                        else:
                            temp_files.remove(file)
                    else:
                        file["is_custom_page"] = True
                        file["relative_path"] = file["path"].replace(
                            path, "").strip("/")
                else:
                    temp_files.remove(file)
        else:
            temp_files = []

    data = {"files": temp_files[(page - 1) * pre:(page - 1) * pre + pre]}
    data["files"] = datas_paging(pre=pre, page_num=page,
                                 data_cnt=len(temp_files), datas=data["files"])
    data["files"]["current_theme"] = theme_name
    return data


def get_static_file_content():
    """
    获取静态文件内容, 如html文件
    :return:
    """
    filename = request.argget.all('filename', "index").strip("/")
    file_path = request.argget.all('file_path', "").strip("/")
    theme_name = request.argget.all("theme_name")

    s, r = arg_verify([(gettext("theme name"), theme_name)], required=True)
    if not s:
        return r
    path = os.path.join(
        THEME_TEMPLATE_FOLDER, theme_name)
    file = "{}/{}/{}".format(path, file_path, filename)
    if not os.path.exists(file) or THEME_TEMPLATE_FOLDER not in file:
        data = {"msg": gettext("File not found,'{}'").format(file),
                "msg_type": "w", "custom_status": 404}
    else:
        with open(file) as wf:
            content = wf.read()
        data = {
            "content": content,
            "file_relative_path": file_path.replace(
                path,
                "").strip("/")}
    return data


def edit_static_file():
    """
    静态文件编辑, 如html文件
    :return:
    """
    filename = request.argget.all('filename', "index").strip("/")
    file_path = request.argget.all('file_path', "").strip("/")
    content = request.argget.all('content', "")
    theme_name = request.argget.all("theme_name")

    s, r = arg_verify([(gettext("theme name"), theme_name)], required=True)
    if not s:
        return r
    path = os.path.join(
        THEME_TEMPLATE_FOLDER, theme_name)
    file = "{}/{}/{}".format(path, file_path, filename)

    if not os.path.exists(file):
        data = {"msg": gettext("File does not exist can not be edited,'{}'").format(
            file), "msg_type": "w", "custom_status": 404}
    else:
        with open(file, "w") as wf:
            wf.write(content)

        data = {"msg": gettext("Saved successfully"),
                "msg_type": "s", "custom_status": 201}
    return data
