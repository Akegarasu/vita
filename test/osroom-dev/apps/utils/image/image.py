#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from PIL import Image


class ImageCompression:

    def __init__(self, image_path, save_path):
        self.im = Image.open(image_path)
        self.image_path = image_path
        self.save_path = save_path

    def isometric(self, w=0, h=0):
        """
        等比例缩放
        :param w: 为0则按h于原图h比例
        :param h: 为0则按w于原图h比例
        :return:
        """
        if w:
            h = w / self.im.size[0] * self.im.size[1]
        elif h:
            w = h / self.im.size[1] * self.im.size[0]
        self.custom_pixels(w=w, h=h)

    def custom_pixels(self, w, h):
        """
        自定义宽高
        :param w:宽
        :param h: 高
        :return:
        """

        self.im.resize(
            (int(w), int(h)), Image.ANTIALIAS).save(
            self.save_path, self.im.format)
