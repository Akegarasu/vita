#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import Flask
from apps.core.flask.response import OsrResponse


class OsrApp(Flask):
    response_class = OsrResponse
