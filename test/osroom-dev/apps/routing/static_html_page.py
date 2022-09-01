#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2019/11/20 12:44
# @Author : Allen Woo
import os
import re
from flask import render_template, abort, g, request, redirect

from apps.app import cache
from apps.core.blueprint import static_html_view
from apps.core.utils.get_config import get_config
from apps.modules.global_data.process.global_data import get_global_site_data
from apps.modules.post.process.post import get_post, get_posts


@cache.cached(timeout=86400, key_base64=False, db_type="redis")
def get_post_page_nums():

    data = get_posts(page=1)
    page_nums = list(range(1, data["posts"]["page_total"] + 1))
    return page_nums


def static_html(path):
    if get_config("seo", "SPIDER_RECOGNITION_ENABLE"):
        g.site_global = dict(g.site_global, **get_global_site_data(req_type="view"))
        r = re.match(r"{}/post/(.+)".format(static_html_view.url_prefix.strip("/")), path)
        if r:
            return post_page(r.groups()[-1])

        r = re.match(r"{}/posts/([0-9]+)$".format(static_html_view.url_prefix.strip("/")), path)
        if r:
            return posts_page(int(r.groups()[-1]))
    else:
        abort(404)


def post_page(post_id):
    """
    GET:
        通用视图函数,那些公共的页面将从此进入
        :param post_id: 文章id
        :return:
    """
    theme_pages = get_config("seo", "THEME_PAGE_FOR_STATIC_PAGE")
    post_url = None
    if "post_page" in theme_pages:
        # 主题post页面路由
        post_url = theme_pages["post_page"].replace("<id>", post_id)

    user_agent = request.headers.get("User-Agent").lower()
    is_spider_bot = False
    for bot in get_config("seo", "SUPPORTED_SPIDERS"):
        if bot.lower() in user_agent:
            # 是搜索引擎蜘蛛
            is_spider_bot = True
            break
    if is_spider_bot:
        # 是搜索引擎蜘蛛
        data = get_post(post_id=post_id)
        absolute_path = os.path.abspath("{}/post.html".format(static_html_view.template_folder))
        if not os.path.isfile(absolute_path):
            abort(404)
        # 使用osroom静态页面
        return render_template('post.html', data=data)
    elif post_url:
        # 使用主题动态页面
        return redirect(post_url)

    abort(404)


def posts_page(page):
    """
    GET:
        通用视图函数,那些公共的页面将从此进入
        :param post_id: 文章id
        :return:
    """
    data = get_posts(page=page)
    data["posts"]["page_nums"] = list(range(1, data["posts"]["page_total"]+1))
    absolute_path = os.path.abspath("{}/posts.html".format(static_html_view.template_folder))
    if not os.path.isfile(absolute_path):
        abort(404)
    return render_template('posts.html', data=data)
