#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os
import random
from uuid import uuid1
import time
from apps.core.plug_in.manager import plugin_manager
from apps.utils.upload.file_up import file_del, local_file_del
from apps.utils.upload.get_filepath import get_file_url
from apps.app import mdbs
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from apps.core.utils.get_config import get_config
from apps.configs.sys_config import STATIC_PATH
from apps.utils.verify.captcha import ImageCaptcha


class CreateImgCode(object):

    def __init__(self, size_width, size_height, background):
        """
        初始化图片大小背景
        :param size_width:  图片大小宽
        :param size_height: 图片大小高
        :param background: 背景颜色
        """
        self.size = (size_width, size_height)
        self.background = background
        self.random_color = RandomColor()

    def create_pic(self):
        """
        创建一张图片
        """

        self.width, self.height = self.size
        self.img = Image.new("RGB", self.size, self.background)

        # 画笔
        self.draw = ImageDraw.Draw(self.img)

    def create_point(self, num):
        """
        画点
        :param num: 数量
        :return:
        """
        for i in range(num):
            self.draw.point(
                (random.randint(
                    0, self.width), random.randint(
                    0, self.height)), fill=self.random_color.random_color())

    def create_line(self, num):
        """
        画干扰线条
        :param num: 数量
        :return:
        """
        for i in range(num):
            self.draw.line(
                [
                    (random.randint(
                        0, self.width), random.randint(
                        0, self.height)), (random.randint(
                            0, self.width), random.randint(
                            0, self.height))], fill=self.random_color.random_color())

    def create_text(self, font_type, font_size, string):
        """
        把code画入图片
        :param font_type: 字体路径
        :param font_size: 字体大小
        :param string: 字符串
        :return:
        """

        font = ImageFont.truetype(font_type, font_size)
        str_list = list(string)
        # 横向边距
        w_margin = 15
        # 宽度字符间隔
        w_interval = (self.size[0] - w_margin * 2) / (len(str_list) - 1)
        # 纵向边距
        h_margin = 10
        # 高度起点最低坐标

        h_scope = (self.size[1]-h_margin*2)-font_size
        for t, c in enumerate(str_list):
            h = random.randint(10, h_scope)
            self.draw.text((w_interval * t + 10, h), c,
                           font=font,
                           fill=self.random_color.random_color2())

    def istortion_shift(self):
        """
        给图片上的文字, 干扰线条再作扭曲, 移位等
        :return:
        """
        self.img = self.img.filter(ImageFilter.EDGE_ENHANCE_MORE)


class RandomColor:

    """
    验证码生成
    """

    def random_color(self):
        """
        随机生成字符颜色
        :return:
        """
        return (
            random.randint(
                64, 255), random.randint(
                64, 255), random.randint(
                64, 255))

    def random_color2(self):
        """
        随机生成用于干扰颜色
        :return:
        """
        return (
            random.randint(
                32, 180), random.randint(
                64, 180), random.randint(
                64, 180))


def random_char():
    """
    随机生成一个字母或数字字符
    :return:
    """

    i = random.randint(1, 3)
    if i == 1:
        an = random.randint(97, 122)
    elif i == 2:
        an = random.randint(65, 90)
    else:
        an = random.randint(48, 57)
    return chr(an)


def create_img_code(interference=0):
    """
    生成验证码
    difficulty: 数值越高, 越难辨别,最小为10
    :return:
    """
    # 240 x 60:
    # 每次生成验证码的同时,我们删除本地过期验证码
    vercode_del(expiration_time=get_config("verify_code", "EXPIRATION"))

    _str = ""
    for t in range(4):
        c = random_char()
        _str = "{}{}".format(_str, c)

    # 使用ImageCaptcha验证码生成程序
    image = ImageCaptcha()
    image.generate(_str)

    # 保存路径
    local_dirname = get_config("verify_code", "IMG_CODE_DIR")
    save_dir = "{}/{}".format(STATIC_PATH, local_dirname).replace("//", "/")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    code_img = '{}__{}.png'.format(time.time(), uuid1())
    save_img = '{}/{}'.format(save_dir, code_img)
    image.write(_str, save_img)

    # osroom 验证码程序
    # max_in = get_config("verify_code", "MAX_IMG_CODE_INTERFERENCE")
    # min_in = get_config("verify_code", "MIN_IMG_CODE_INTERFERENCE")
    # if interference < 10:
    #
    #     if min_in < 10:
    #         min_in = 10
    #     if min_in > max_in:
    #         temp_max_in = max_in
    #         max_in = min_in
    #         min_in = temp_max_in
    #     else:
    #         min_in = 10
    #         max_in = 30
    #     interference = random.randint(min_in, max_in)
    #
    # # 验证码尺寸
    # width = 60 * 4
    # height = 60
    # pic = CreateImgCode(width, height, 'white')
    # pic.create_pic()
    # pic.create_point(interference * 50)
    # pic.create_line(interference * 3)

    # 生成随机码写入
    # _str = ""
    # for t in range(4):
    #     c = random_char()
    #     _str = "{}{}".format(_str, c)
    # pic.create_text(FONT_PATH, 24, _str)
    #
    # # 扭曲
    # # pic.istortion_shift()
    #
    # 保存路径
    # local_dirname = get_config("verify_code", "IMG_CODE_DIR")
    # save_dir = "{}/{}".format(STATIC_PATH, local_dirname).replace("//", "/")
    # if not os.path.exists(save_dir):
    #     os.makedirs(save_dir)
    # code_img = '{}__{}.jpg'.format(time.time(), uuid1())
    # save_img = '{}/{}'.format(save_dir, code_img)
    #
    # # 保存
    # pic.img.save(save_img, 'jpeg')

    # 检图床插件
    data = plugin_manager.call_plug(
        hook_name="file_storage",
        action="upload",
        localfile_path=save_img,
        filename="{}/{}".format(local_dirname, code_img)
    )

    if data == "__no_plugin__":

        code_url_info = {"key": code_img, "type": "local"}
    else:
        code_url_info = data
        # 使用了第三方插件存储,则删除本地验证码
        local_file_del(path=save_img)

    _code = {
        'url': code_url_info,
        'str': _str,
        'time': time.time(),
        "type": "image"}
    mdbs["web"].db.verify_code.insert_one(_code)
    _code.pop('_id')
    _code.pop('str')
    _code['img_url_obj'] = _code['url']
    _code['url'] = get_file_url(code_url_info, save_dir=local_dirname)
    return _code


def verify_image_code(code_img_obj, code):
    """
    验证验证码
    :param code_img_key:
    :param code:
    :return:
    """
    r = False
    if "key" not in code_img_obj:
        return r

    expiration_time = get_config("verify_code", "EXPIRATION")
    code_data = mdbs["web"].db.verify_code.find_one(
        {'url.key': code_img_obj["key"], "type": "image"})
    if code_data:
        if code.lower() == code_data['str'].lower(
        ) and time.time() - code_data['time'] < expiration_time:
            r = True
    return r


def vercode_del(file_url_obj=None, expiration_time=None):
    """
    删验证码
    :param url:
    :param expiration_time:顺便删除过期的验证码
    :return:
    """

    if file_url_obj:
        file_del(file_url_obj=file_url_obj)
        mdbs["web"].db.verify_code.delete_many(
            {'url.key': file_url_obj["key"], "type": "image"})

    if expiration_time:
        codes = mdbs["web"].db.verify_code.find(
            {'time': {"$lt": time.time() - expiration_time}, "type": "image"})
        for code in codes:
            file_del(code["url"])
            mdbs["web"].db.verify_code.delete_one({'_id': code["_id"]})
