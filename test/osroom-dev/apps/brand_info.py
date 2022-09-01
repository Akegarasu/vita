#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import platform
import os
from PIL import Image
from apps.configs.sys_config import STATIC_PATH, VERSION
from apps.develop_run_options import start_info_print


def start_info():
    """
    启动时, 打印系统信息
    :return:
    """

    width = 30
    height = 15
    logo_path = "{}/sys_imgs/osroom-logo-white.png".format(STATIC_PATH)
    if os.path.exists(logo_path):
        im = Image.open(logo_path)
        im = im.resize((width, height), Image.NEAREST)
        txt = ""
        for i in range(height):
            txt += " " * 15
            for j in range(width):
                ch = get_char(*im.getpixel((j, i)))
                if ch == "*":
                    ch = "\033[1;37m{}\033[0m".format(ch)
                else:
                    ch = "\033[1;33m{}\033[0m".format(ch)
                txt += ch
            txt += '\n'
        start_info_print(txt)

    version = VERSION
    info = """
    Welcome to use the osroom.
    osroom v{}
    osroom website: \033[1;34m https://osroom.com \033[0m
    Project code download: \033[1;34m https://github.com/osroom/osroom \033[0m
    License: BSD3
    The operating system: {}
    """.format(version, platform.system())
    start_info_print(info)


def get_char(r, b, g, alpha=256):

    ascii_char = list("*. ")
    if alpha == 0:
        return ' '
    length = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)

    unit = (512.0 + 1) / length
    return ascii_char[int(gray / unit)]
