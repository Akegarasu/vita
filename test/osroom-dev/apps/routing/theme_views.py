#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os
import time
from apps.app import csrf
from apps.core.blueprint import theme_view, static_html_view
from flask import render_template, request, send_file, g
from werkzeug.exceptions import abort
from apps.core.flask.permission import page_permission_required
from apps.core.utils.get_config import get_config
from apps.modules.global_data.process.global_data import get_global_site_data
from apps.routing.static_html_page import static_html, get_post_page_nums
from apps.utils.format.time_format import time_to_utcdate


# homepage
@csrf.exempt
@theme_view.route('/', methods=['GET', 'POST'])
@page_permission_required()
def index():
    return get_render_template("index")


# other
@csrf.exempt
@theme_view.route('/<path:path>', methods=['GET'])
@page_permission_required()
def pages(path):
    """
    GET:
        通用视图函数,那些公共的页面将从此进入
        :param path:
        :return:
    """
    if path.startswith(static_html_view.url_prefix.strip("/")):
        return static_html(path)
    return get_render_template(path.rstrip("/"))


def get_render_template_view(path, theme_name):
    """
    根据路由path,返回一个render_template
    :param path:
    :return:
    """
    # 拼接当前主题目录
    path = "{}/pages/{}".format(theme_name, path)
    absolute_path = os.path.abspath(
        "{}/{}.html".format(theme_view.template_folder, path))
    if not os.path.isfile(absolute_path):
        path = "{}/index".format(path)
        absolute_path = os.path.abspath(
            "{}/{}.html".format(theme_view.template_folder, path))
        if not os.path.isfile(absolute_path):
            abort(404)

    data = dict(request.args.items())
    g.site_global = dict(g.site_global,
                         **get_global_site_data(req_type="view"))
    return render_template('{}.html'.format(path), data=data)


def get_render_template(path):
    """
    根据路由path,返回一个render_template
    :param path:
    :return:
    """
    # 拼接当前主题目录
    path = "{}/pages/{}".format(get_config("theme", "CURRENT_THEME_NAME"), path)
    absolute_path = os.path.abspath(
        "{}/{}.html".format(theme_view.template_folder, path))
    if not os.path.isfile(absolute_path):
        path = "{}/index".format(path)
        absolute_path = os.path.abspath(
            "{}/{}.html".format(theme_view.template_folder, path))
        if not os.path.isfile(absolute_path):
            abort(404)

    data = dict(request.args.items())
    g.site_global = dict(g.site_global, **get_global_site_data(req_type="view"))
    return render_template('{}.html'.format(path), data=data)


def get_render_template_email(path, params):
    """
        根据路由path,返回一个render_template
        :param path:
        :return:
        """
    # 拼接当前主题目录
    path = "{}/pages/{}".format(get_config("theme",
                                           "CURRENT_THEME_NAME"), path)
    absolute_path = os.path.abspath(
        "{}/{}.html".format(theme_view.template_folder, path))
    if not os.path.isfile(absolute_path):
        path = "{}/index".format(path)
        absolute_path = os.path.abspath(
            "{}/{}.html".format(theme_view.template_folder, path))
        if not os.path.isfile(absolute_path):
            abort(404)

    g.site_global = dict(g.site_global,
                         **get_global_site_data(req_type="view"))
    return render_template('{}.html'.format(path), data=params)


@csrf.exempt
@theme_view.route('/robots.txt', methods=['GET'])
def robots():
    """
    robots.txt
    :return:
    """
    absolute_path = "{}/{}/pages/robots.txt".format(
        theme_view.template_folder, get_config(
            "theme", "CURRENT_THEME_NAME"))
    return send_file(absolute_path)


# sitemap
@csrf.exempt
@theme_view.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """
    sitemap.xml
    :return:
    """
    ut = time.time()
    content = ""
    host_url = request.host_url
    for n in get_post_page_nums():
        content = """
{content}
<url>
    <loc>{domain}st-html/posts/{page}</loc>
    <lastmod>{date}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
</url>""".format(
            content=content,
            page=n,
            domain=host_url,
            date=time_to_utcdate(ut, "%Y-%m-%d"),
            freq="daily",
            priority="0.6"
        )

    content = """<?xml version="1.0" encoding="utf-8"?>
<urlset  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {content}
</urlset>""".format(content=content)
    absolute_path = os.path.abspath("{}/sitemap.xml".format(static_html_view.template_folder))
    with open(absolute_path, "w") as wf:
        wf.write(content)
    return send_file(absolute_path)
