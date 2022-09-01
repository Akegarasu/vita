#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.core.flask.login_manager import osr_login_required
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.user.process.avatar_upload import avatar_upload


@api.route('/account/upload/avatar', methods=['PUT'])
@osr_login_required
@permission_required(use_default=False)
def api_avatar_upload():
    """
    PUT
        头像上传
        注意:虽然服务的提供图片裁剪功能，由于耗费服务器资源,非必要情况下请不要使用，请再客户端裁剪好再上传.
        为了防止恶意使用裁剪功能，可以在管理端中设置(upload)中关闭上传文件裁剪功能
        *提供2种上传方式*
        1.以常规文件格式上传
        upfile:<img file>，头像文件
        preview_w:<int>, 图片预览宽度
        tailoring:<dict>, (裁剪功能开启后才能使用),裁剪尺寸，格式:{x:12, y:12, height:100, width:100, rotate:0}
            x和ｙ为裁剪位置，x距离左边距离, y距离上边距离, width截图框的宽，　height截图框的高

        2.以base64编码上传
        imgfile_base:<str>,以base64编码上传文件


    :return:
    """
    data = avatar_upload()
    return response_format(data)
