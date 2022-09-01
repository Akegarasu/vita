#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os
from flask import send_file, request, render_template, g
from werkzeug.exceptions import abort
from apps.app import csrf
from apps.configs.sys_config import ADMIN_STATIC_FOLDER, TEMP_STATIC_FOLDER
from apps.core.blueprint import static, theme_view, admin_static_file
from apps.core.flask.permission import page_permission_required
from apps.core.utils.get_config import get_config
from apps.modules.global_data.process.global_data import get_global_site_data
from apps.utils.format.obj_format import str_to_num

from apps.utils.image.image import ImageCompression

"""
 静态文件路由
 提示:
 1. static_size_img：　
    apps/static下图片路由: /static/<regex(r".*\..+"):path>
    参数w,h可指定图片大小
 2. theme_static：
    themes主题static下静态文件路由：/<theme name>/static/<regex(".*"):path>
    参数w,h可指定图片大小
"""


#####################################################
# apps/static静态文件路由
#####################################################
@csrf.exempt
@static.route('/<regex(".+"):path>', methods=['GET'])
@page_permission_required()
def static_file(path):
    """
    apps/static下静态文件获取(本视图函数只针对apps/static下的图片)，apps/static下其他可以直接哟你flask默认的

    注意：图片获取路由(apps/static下)
    参数w,h可指定图片大小
    :param path:原图片路径
    :param w:获取的宽
    :param h:获取的高
    :return:w和ｈ都大于0则返回相应尺寸图片; w和ｈ都等于0则返回原图; 其中一个值大于０则返回以这个值为基础等比缩放图片
    """
    w = str_to_num(request.args.get("w", 0))
    h = str_to_num(request.args.get("h", 0))
    if w or h:
        path_list = os.path.splitext(path.rstrip().rstrip("/"))
        absolute_path = os.path.abspath("{}/{}_w_{}_h_{}{}".format(static.template_folder,
                                                                   path_list[0],
                                                                   w, h, path_list[1]))
        if not os.path.isfile(absolute_path):

            img_path = os.path.abspath(
                "{}/{}".format(static.template_folder, path))
            try:
                imgcs = ImageCompression(img_path, absolute_path)
            except BaseException:
                abort(404)
            if w and h:
                # 自定义长宽
                imgcs.custom_pixels(w, h)
            else:
                # 等比缩放
                imgcs.isometric(w, h)

    else:
        absolute_path = os.path.abspath(
            "{}/{}".format(static.template_folder, path))
        if not os.path.isfile(absolute_path):
            abort(404)
        absolute_path = banel_translate_js_files(
            prefix="static",
            route_relative_path=path,
            absolute_path=absolute_path
        )
    return send_file(filename_or_fp=absolute_path,
                     conditional=True,
                     last_modified=True)


#####################################################
# apps/admin_pages/下静态文件路由
#####################################################

@csrf.exempt
@admin_static_file.route('/<regex(".+"):path>', methods=['GET'])
@page_permission_required()
def admin_static_file(path):
    """
    获取admin_pages下静态文件
    :param path:文件路径
    """
    absolute_path = os.path.abspath("{}/{}".format(
        ADMIN_STATIC_FOLDER,
        path
    ))
    if not os.path.isfile(absolute_path):
        abort(404)
    absolute_path = banel_translate_js_files(
        prefix="adm_static_file",
        route_relative_path=path,
        absolute_path=absolute_path
    )
    return send_file(filename_or_fp=absolute_path,
                     conditional=True,
                     last_modified=True)


#####################################################
# apps/themes/下主题静态文件路由
#####################################################


@csrf.exempt
@theme_view.route('/theme/<theme_name>/static/<regex(".+"):path>', methods=['GET'])
@page_permission_required()
def theme_static_file(path, theme_name=None):
    """
    获取主题下静态文件
    注意:
        theme主题图片获取路由 (目录themes/<theme name>/static下图片)
        1.对于图片,本路由只能获取目录themes/<theme name>/static下定义尺寸图片
        参数w,h可指定图片大小
    :param path:原图片路径
    :param w: 获取的宽
    :param h: 获取的高
    :return:w和ｈ都大于0则返回相应尺寸图片; w和ｈ都等于0则返回原图; 其中一个值大于０则返回以这个值为基础等比缩放图片
    """
    if not theme_name:
        theme_name = get_config("theme", "CURRENT_THEME_NAME")
    w = str_to_num(request.args.get("w", 0))
    h = str_to_num(request.args.get("h", 0))
    if w or h:
        path_list = os.path.splitext(path.rstrip().rstrip("/"))
        absolute_path = os.path.abspath(
            "{}/{}/static/{}_w_{}_h_{}{}".format(
                theme_view.template_folder,
                theme_name,
                path_list[0],
                w,
                h,
                path_list[1]))
        if not os.path.isfile(absolute_path):
            img_path = os.path.abspath(
                "{}/{}/static/{}".format(
                    theme_view.template_folder, theme_name, path))
            try:
                imgcs = ImageCompression(img_path, absolute_path)
            except BaseException:
                abort(404)
            if w and h:
                # 自定义长宽
                imgcs.custom_pixels(w, h)
            else:
                # 等比缩放
                imgcs.isometric(w, h)
    else:
        path = "{}/static/{}".format(theme_name, path)
        absolute_path = os.path.abspath("{}/{}".format(theme_view.template_folder, path))
        if not os.path.isfile(absolute_path):
            abort(404)
        absolute_path = banel_translate_js_files(
            prefix=theme_name,
            route_relative_path=path,
            absolute_path=absolute_path
        )
    return send_file(filename_or_fp=absolute_path,
                     conditional=True,
                     last_modified=True)


def banel_translate_js_files(prefix, route_relative_path, absolute_path):
    """
    Jinja2翻译js
    :param prefix:
    :param route_relative_path:
    :param absolute_path:
    :return:
    """
    if route_relative_path.endswith(".js"):
        # js 翻译
        ori_file_time = os.path.getmtime(absolute_path)
        name = os.path.split(route_relative_path)[-1]

        # 主题页面js或者以osr_开头的js文件给予翻译
        if "osr_page_js" in route_relative_path or name.startswith("osr-"):
            # 使用翻译好的js
            temp_name = "{}{}_{}".format(
                prefix,
                os.path.splitext(route_relative_path)[0].replace("/", "_"),
                g.site_global["language"]["current"])

            absolute_path = "{}/{}.js".format(TEMP_STATIC_FOLDER, temp_name)
            if not os.path.isfile(absolute_path):
                # 不存在翻译文件
                g.site_global = dict(g.site_global, **get_global_site_data(req_type="view"))
                data = dict(request.args.items())
                tr_content = render_template(route_relative_path, data=data)
                with open(absolute_path, "w") as wf:
                    # flask中没找替换翻译js的Jinjia模块. 使用render_template来翻译js文件,
                    wf.write(tr_content)
            else:
                tr_file_time = os.path.getmtime(absolute_path)
                if tr_file_time < ori_file_time:
                    # 翻译文件的最后修改时间小于原文件
                    g.site_global = dict(g.site_global, **get_global_site_data(req_type="view"))
                    data = dict(request.args.items())
                    tr_content = render_template(route_relative_path, data=data)
                    with open(absolute_path, "w") as wf:
                        # flask中没找替换翻译js的Jinjia模块. 使用render_template来翻译js文件,
                        wf.write(tr_content)
            return absolute_path
    return absolute_path
