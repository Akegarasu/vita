#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from apps.core.flask.login_manager import osr_login_required
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.upload.process.upload_file import file_upload


@api.route('/upload/file', methods=['POST'])
@osr_login_required
@permission_required(use_default=False)
def api_file_upload():
    """
    POST
        文件上传
        api返回json数据,格式默认如下:
        {'urls':[<url>, ...,<url>],
         'state':<'success' or 'error'>,
         'msg_type':<'s' or e'>,
         'msg':''
         }

        return_url_key: <str>, 自定义返回数据的urls的key, 默认'urls'
        return_state_key:<str>, 自定义返回数据的状态的key, 默认'state'
        return_success:<str or int>, 自定义返回数据成功的状态的值, 默认'success'
        return_error:<str or int>, 自定义返回数据错误的状态的值, 默认'error'

        prefix:<str>, 默认为“generic/”, 则会将文件放入到generic目录下
        save_temporary_url：<0 or 1>,默认为1, 如果
        :return:
    """

    return_url_key = request.argget.all('return_url_key', "urls")
    return_state_key = request.argget.all('return_state_key', "state")
    return_success = request.argget.all('return_success', "success")
    return_error = request.argget.all('return_error', "error")
    prefix = request.argget.all('prefix', "generic/")
    save_temporary_url = request.argget.all('save_temporary_url', 1)

    data = file_upload(
        return_url_key=return_url_key,
        return_state_key=return_state_key,
        return_success=return_success,
        return_error=return_error,
        save_temporary_url=save_temporary_url,
        prefix=prefix)
    return response_format(data)
