#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.global_data.process.global_data import get_global_media, get_global_site_data


@api.route('/global', methods=['GET'])
@permission_required(use_default=False)
def api_current_global():
    """
    GET:
        获取当前全局数据,包括站点的公开设置, 当前登录用户的基本可公开信息
        :return:
    """
    data = get_global_site_data(req_type="api")
    return response_format(data)


@api.route('/global/media', methods=['GET'])
@permission_required(use_default=False)
def api_get_media():
    """
    GET:
        1.获取指定的多媒体数据
        conditions:<array:dict>, Such as:[{'type':<str>, 'names':<array>, 'name_regex':''}]
            说明:
                type-可以是"text", "image", "video", "audio"
                names-数组,指定要获取数据的name
                name_regex-字符串,获取匹配此正则的media,如果为空值，则不使用正则匹配(空置包括null, None,False, "")
                注意:name 与name_regex不能同时使用,当name_regex非空时，查询自动忽略names
            使用示例：前提在管理端多媒体中存在的内容
            如:首页轮播图片和获取”关于我们“页面的文字内容
            [
                {"type":"image", "names":["home-carousel-1", "home_carousel-2"]},
                {"type":"text", "names":["about-me"]},
                {"type":"image", "name_regex":"test-[0-9]+"}
            ]

        2.获取指定category的多媒体
        category_name:<array> category name, 可同时指定多个category name, 使用数组
        category_user_id:<str>, 为空则表示获取站点官方的多媒体
        category_type:<str>, 可选"text", "image", "video", "audio"
        page:<int>, 第几页, 默认1
        pre:<int>, 每页几条数据, 默认8

        3.根据id 获取
        media_id:<str>

        :return:
    """

    data = get_global_media(dbname="web", collname="media")
    return response_format(data)


@api.route('/global/theme-data/display', methods=['GET'])
@permission_required(use_default=False)
def api_get_theme_display_data():
    """
    GET:
        1.获取主题展示用的多媒体数据
        conditions:<array:dict>, Such as:[{'type':<str>, 'names':<array>, 'name_regex':''}]
            说明:
                type-可以是"text", "image", "video", "audio"
                names-数组,指定要获取数据的name
                name_regex-字符串,获取匹配此正则的media,如果为空值，则不使用正则匹配(空置包括null, None,False, "")
                注意:name 与name_regex不能同时使用,当name_regex非空时，查询自动忽略names
            使用示例：前提在管理端多媒体中存在的内容
            如:首页轮播图片和获取”关于我们“页面的文字内容
            [
                {"type":"image", "names":["home-carousel-1", "home_carousel-2"]},
                {"type":"text", "names":["about-me"]},
                {"type":"image", "name_regex":"test-[0-9]+"}
            ]

        :return:
    """

    data = get_global_media(dbname="sys", collname="theme_display_setting")
    return response_format(data)
