#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo

from flask import render_template_string


def render_absolute_path_template(path, **context):
    """
    渲染绝对路径下template文件
    :param path:
    :param context:
    :return:
    """
    with open(path) as rhtml:
        source = rhtml.read()
    return render_template_string(source=source, **context)

