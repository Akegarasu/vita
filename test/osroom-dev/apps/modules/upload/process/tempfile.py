#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from apps.app import mdbs
from apps.utils.upload.file_up import file_del
from apps.utils.upload.get_filepath import get_file_url


def clean_tempfile(user_id, type, old_file=[], keey_file=[]):
    """
    清理数据库中tempfile文档中保存的临时文件
    :param user_id: 用户ID
    :param type: 临时文件类型
    :param old_file: 已存在, 但不知是否在保留文件中的文件
    :param keey_file: 当前临时文件中需要保留的文件
    :return:
    """

    tempfiles = mdbs["web"].db.tempfile.find({"type": type, "user_id": user_id})
    files = []

    # 找出被上传后没有使用的图片:
    temppaths = []
    for tempfile in tempfiles:
        temppaths.extend(tempfile["paths"])

    temppaths.extend(old_file)
    need_rm_files = temppaths[:]
    for img in temppaths:
        path = get_file_url(img)
        if not path:
            continue
        for src in keey_file:
            if not src:
                continue
            if path.lower() in src.lower():
                files.append(img)
                need_rm_files.remove(img)
                break

    # 文章中没有的图片就删除
    for rf in need_rm_files:
        file_del(rf)

    # 更tempfile数据库的的数据
    mdbs["web"].db.tempfile.delete_many({"type": type, "user_id": user_id})
    return files
