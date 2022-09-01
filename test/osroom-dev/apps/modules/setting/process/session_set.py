#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request, session
from flask_babel import gettext

from apps.app import rest_session
from apps.core.utils.get_config import get_config


def language_set():

    lan = request.argget.all('language', "zh_CN")
    session["language"] = lan
    if request.headers.get('OSR-ClientId'):
        rest_session.set("language", lan)
    else:
        session["language"] = lan

    if lan in list(get_config('babel', 'LANGUAGES').keys()):
        data = {
            "msg_type": "s",
            "msg": gettext("Set up language success"),
            "custom_status": 201}
    else:
        data = {
            "msg_type": "e",
            "msg": gettext("Does not support this language"),
            "custom_status": 400}

    return data
