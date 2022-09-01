#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os

import time
from flask import render_template, url_for, g

from apps.core.blueprint import theme_view, admin_view
from apps.core.template.template import render_absolute_path_template
from apps.core.utils.get_config import get_config
from apps.utils.format.time_format import time_to_utcdate


def get_email_html(data, template_path=None):
    """
    获取发送邮件使用的html模板
    :param data: 需要再模板中使用的数据, 使用Jinjia2
            格式:{"title": "标题",
                "body": "正文, 可以使用html标签",
                "other_info":"其他信息, 可以使用html标签",
                }
    :return:
    """

    # 查找主题邮件发送html模板
    data["app_name"] = get_config("email", "APP_NAME")
    data["app_logo_url"] = get_config("email", "APP_LOG_URL")
    conf_site_url = get_config("site_config", "SITE_URL")
    if conf_site_url:
        data["site_url"] = url_for("theme_view.index")
    else:
        data["site_url"] = url_for("theme_view.index")
    data["utc_time"] = time_to_utcdate(
        time_stamp=time.time(),
        tformat="%Y-%m-%d %H:%M:%S")

    if template_path:
        path = "{}/{}".format(
            g.get_config("theme", "CURRENT_THEME_NAME"),
            template_path
        )
    else:
        path = "{}/pages/module/email/send-temp.html".format(
            g.get_config("theme", "CURRENT_THEME_NAME")
        )
    absolute_path = os.path.abspath(
        "{}/{}".format(theme_view.template_folder, path))
    if os.path.isfile(absolute_path):
        html = render_template(path, data=data)
    else:
        # 主题不存页面,使用系统自带的页面
        path = "{}/module/email/send-temp.html".format(
            admin_view.template_folder)
        html = render_absolute_path_template(path, data=data)
    return html
