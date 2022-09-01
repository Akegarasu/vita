#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from tld import get_tld


def get_domain(url):
    """
    获取url中的全域名
    :param url:
    :return:
    """
    try:
        res = get_tld(url, as_object=True)
    except Exception:
        return False
    return "{}.{}".format(res.subdomain, res.tld)
