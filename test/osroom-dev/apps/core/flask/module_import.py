#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from importlib import import_module


def module_import(modules):

    for module in modules:
        import_module(module)
