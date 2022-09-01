#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from lxml import etree


def richtext_extract_img(richtext=""):

    # 获取富文本中使用的图片
    s = etree.HTML(richtext.lower())
    srcs = s.xpath("//img/@src")
    return srcs
