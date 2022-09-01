#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os
from apps.core.flask.login_manager import osr_login_required
from apps.app import csrf
from apps.core.blueprint import admin_view
from flask import render_template, request, g
from werkzeug.exceptions import abort
from apps.core.flask.permission import adm_page_permission_required
from apps.modules.global_data.process.global_data import get_global_site_data


@csrf.exempt
@admin_view.route('/', methods=['GET'])
@osr_login_required
@adm_page_permission_required()
def index():
    return get_render_template("index")


@csrf.exempt
@admin_view.route('/sign-in', methods=['GET'])
def sign_in():
    return get_render_template("sign-in")


@csrf.exempt
@admin_view.route('/sign-up', methods=['GET'])
def sign_up():
    return get_render_template("sign-up")


@csrf.exempt
@admin_view.route('/recover-password', methods=['GET'])
def recover_password():
    return get_render_template("recover-password")


@csrf.exempt
@admin_view.route('/<path:path>', methods=['GET'])
# 除以上页面外, 管理端所有页面都必须登录访问
@osr_login_required
@adm_page_permission_required()
def pages(path):
    """
    GET:
        通用视图函数
        :param path:
        :return:
    """
    return get_render_template(path.rstrip("/"))


def get_render_template(path):
    """
    render_template
    :param path:
    :return:
    """

    absolute_path = os.path.abspath(
        "{}/{}.html".format(admin_view.template_folder, path))
    if not os.path.isfile(absolute_path):
        path = "{}/index".format(path)
        absolute_path = os.path.abspath(
            "{}/{}.html".format(admin_view.template_folder, path))
        if not os.path.isfile(absolute_path):
            abort(404)
    data = dict(request.args.items())
    g.site_global = dict(g.site_global,
                         **get_global_site_data(req_type="view"))
    return render_template('{}.html'.format(path), data=data)
