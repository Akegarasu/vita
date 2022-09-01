#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from apps.core.flask.login_manager import osr_login_required

from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.media.process.media import add_media, get_media, edit_media, del_media, get_medias


@api.route('/admin/upload/media-file', methods=['GET', "POST", "PUT", "DELETE"])
@osr_login_required
@permission_required()
def api_add_media():
    """
    GET
        1.获取多个多媒体信息
        file_type:<str>, 文件类型,可选"image", "video", "audio", "other"
        category_id:<str>, 分类id, 获取默认分类使用"default"作为category_id, 不传入此参数则表示获取全部
        keyword:<str>,搜索用
        page:<int>, 第几页, 默认1
        pre:<int>, 每页几条数据, 默认12
        sort:<array>,排序, 1表示升序, -1表示降序.如:
            按时间降序 [{"time":-1}]
            按时间升序 [{"time", 1}]
            默认时按时间降序, 也可以用其他字段排序

        2.获取1个信息
        id:<str>,id

    POST
        添加媒体

        name:<str>, 名字
        link:<str>, 链接, 用于展示的时候跳转链接
        link_name:<str>,链接名字
        link_open_new_tab:<str>,链接是否打开新标签
        title:<str>, 展示的标题
        name:<str>, 展示时需要显示的文字
        text:<str>
        text_html:<str>, text的html格式(富文本)
        type:<str>, 文件类型,可选"image", "video", "audio", "text","other"
        category_id:<str>, 分类id

        **如果需要上传文件,还需要一下参数:

        batch:<int>, 0 or 1, default:0, 为1表示批量上传.
        return_url_key: <str>, 自定义返回数据的urls的key, 默认'urls'
        return_state_key:<str>, 自定义返回数据的状态的key, 默认'state'
        return_success:<str or int>, 自定义返回数据成功的状态的值, 默认'success'
        return_error:<str or int>, 自定义返回数据错误的状态的值, 默认'error'

         **注意: 如果后台获取有文件上传，则表示只上传文件
        上传文件返回数据格式默认如下:
        {'urls':[<url>, ...,<url>],
         'state':<'success' or 'error'>,
         'msg_type':<'s' or e'>,
         'msg':''
         }

    PUT
        编辑多媒体信息
        id:<str>,要编辑的media id
        category_id:<str>,要编辑的文件的分类id, 如果不修改分类可以不提交
        name:<str>
        link:<str>, 链接
        link_name:<str>,链接名字
        link_open_new_tab:<str>,链接是否打开新标签
        title:<str>
        text:<str>
        text_html:<str>, text的html格式(富文本)

        **如果只更新文件(如图片),还需要一下参数:
        batch:<int>, 0 or 1, default:0, 为1表示批量上传.
        return_url_key: <str>, 自定义返回数据的urls的key, 默认'urls'
        return_state_key:<str>, 自定义返回数据的状态的key, 默认'state'
        return_success:<str or int>, 自定义返回数据成功的状态的值, 默认'success'
        return_error:<str or int>, 自定义返回数据错误的状态的值, 默认'error'

        **注意: 如果后台获取有文件上传，则表示只上传文件
        上传文件返回数据格式默认如下:
        {'urls':[<url>, ...,<url>],
         'state':<'success' or 'error'>,
         'msg_type':<'s' or e'>,
         'msg':''
         }

    DELETE
        删除多媒体文件
        ids:<array>,要删除的文件的id
        :return:
    """
    if request.c_method == "GET":
        if request.argget.all("id"):
            data = get_media(0)
        else:
            data = get_medias(0)

    elif request.c_method == "POST":
        data = add_media(0)
    elif request.c_method == "PUT":
        data = edit_media(0)
    elif request.c_method == "DELETE":
        data = del_media(0)
    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)
