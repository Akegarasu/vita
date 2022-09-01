#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2020/03/22 10:40
# @Author : Allen Woo
import os

from apps.app import csrf
from apps.core.blueprint import theme_view, static_html_view, admin_view
from flask import g, abort, request, render_template
from apps.core.flask.permission import page_permission_required
from apps.core.utils.get_config import GetConfig, get_config
from apps.modules.global_data.process.global_data import get_global_site_data
from apps.routing.static_html_page import static_html
from apps.routing.theme_views import get_render_template_view


@csrf.exempt
@theme_view.route('/theme/view/<name>/<path:path>', methods=['GET'])
@page_permission_required()
def view_pages(name, path):
    """
    GET:
        通用视图函数,那些公共的页面将从此进入(主题预览用)
        :param path:
        :return:
    """
    fixed_value = {
        "theme": {
            "CURRENT_THEME_NAME": name
        }
    }
    get_conf = GetConfig(fixed_value=fixed_value)
    g.get_config = get_conf.get_config_fixed
    if path.startswith(static_html_view.url_prefix.strip("/")):
        return static_html(path)
    return get_render_template_view(path.rstrip("/"), name)


# 站外链接
@csrf.exempt
@theme_view.route('/link-unaudited', methods=['GET'])
def link_unaudited():
    """
    GET:
        非白名单链接确认页面
        :param path:
        :return:
    """
    path = "link-unaudited"
    # 查找当前主题是否有此页面
    theme_path = "{}/pages/{}".format(get_config("theme", "CURRENT_THEME_NAME"), path)
    absolute_path = os.path.abspath("{}/{}.html".format(theme_view.template_folder, theme_path))
    if not os.path.isfile(absolute_path):
        # 使用系统自带页面
        absolute_path = os.path.abspath("{}/{}.html".format(admin_view.template_folder, path))
        if not os.path.isfile(absolute_path):
            abort(404)
    data = dict(request.args.items())
    g.site_global = dict(g.site_global, **get_global_site_data(req_type="view"))
    return render_template('{}.html'.format(path), data=data)
