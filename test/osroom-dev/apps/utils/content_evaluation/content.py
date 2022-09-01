#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask_login import current_user
from apps.core.plug_in.manager import plugin_manager
from apps.core.utils.get_config import get_config


def content_inspection_text(content):
    """
    文本内容鉴定
    :param content:
    :return:
    """
    if get_config("content_inspection", "TEXT_OPEN"):
        # 调用内容审核插件
        data = plugin_manager.call_plug(
            "content_inspection_text", content=content)
        if data == "__no_plugin__":
            if current_user.is_authenticated and current_user.is_staff:
                return {"score": 0, "label": "no_plugin"}
            else:
                return {"score": 100, "label": "no_plugin"}
        else:
            return data
    else:
        return {"score": 0, "label": "detection_off"}


def content_inspection_image(url):
    """
    图片鉴定
    :param url:图片url
    :return:
    """
    if get_config("content_inspection", "IMAGE_OPEN"):
        # 调用内容审核插件
        data = plugin_manager.call_plug("content_inspection_image", url=url)
        if data == "__no_plugin__":
            if current_user.is_staff:
                return {"score": 0, "label": "no_plugin"}
            else:
                return {"score": 100, "label": "no_plugin"}
        else:
            return data
    else:
        return {"score": 0, "label": "detection_off"}


def content_inspection_video(url):
    """
    视频鉴定
    :param url:视频url
    :return:
    """
    if get_config("content_inspection", "VEDIO_OPEN"):
        # 调用内容审核插件
        data = plugin_manager.call_plug("content_inspection_video", url=url)
        if data == "__no_plugin__":
            if current_user.is_staff:
                return {"score": 0, "label": "no_plugin"}
            else:
                return {"score": 100, "label": "no_plugin"}
        else:
            return data
    else:
        return {"score": 0, "label": "detection_off"}


def content_inspection_audio(url):
    """
    音频鉴定
    :param url:音频url
    :return:
    """
    if get_config("content_inspection", "AUDIO_OPEN"):
        # 调用内容审核插件
        data = plugin_manager.call_plug("content_inspection_audio", url=url)
        if data == "__no_plugin__":
            if current_user.is_staff:
                return {"score": 0, "label": "no_plugin"}
            else:
                return {"score": 100, "label": "no_plugin"}
        else:
            return data
    else:
        return {"score": 0, "label": "detection_off"}
