#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import base64
import glob
import shutil
import urllib
from uuid import uuid1
import time
from PIL import Image
import os

from celery_once import QueueOnce

from apps.app import celery
from apps.configs.sys_config import STATIC_PATH, VIOLATION_IMG_PATH
from apps.core.plug_in.manager import plugin_manager
from apps.core.utils.get_config import get_config
from apps.utils.content_evaluation.content import content_inspection_image
from apps.utils.format.time_format import time_to_utcdate
from apps.utils.upload.get_filepath import get_file_url, get_localfile_path


def file_up(uploaded_files, prefix="", file_name=None, tailoring=None):
    """
     文件上传
    :param uploaded_files: 数组, 上传文件对象
    :param prefix: 给文件名加前缀, 如果prefix中有"/"，则系统也会自动根据/来建目录
    :param file_name:如果file_name是这样的post-img/xxxx-xxx-xxx.jpg，则系统也会自动根据/来建目录
    :return:
    """
    if not uploaded_files:
        return None

    keys = []
    for file in uploaded_files:
        if file:
            if not allowed_file(file.filename):
                key = None
            else:
                file_format_name = file.filename.rsplit('.', 1)[1].lower()

                key = upload_file(
                    file_name=file_name,
                    file_format=file_format_name,
                    file=file,
                    tailoring=tailoring,
                    prefix=prefix)
            keys.append(key)
    call_file_detection.apply_async(
        kwargs={
            "files_file_url_obj": keys
        }
    )
    return keys


def fileup_base_64(uploaded_files, file_name=None, prefix=""):
    """
     文件以base64编码上传上传
    :param uploaded_files: 数组
    :param bucket_var: 保存图片服务器空间名的变量名, 如AVA_B
    :param file_name:
    :return:
    """
    if not uploaded_files:
        return None

    keys = []
    for file_base in uploaded_files:
        if file_base:
            # data:image/jpeg
            file_format = file_base.split(";")[0].split("/")[-1]
            imgdata = base64.b64decode(file_base.split(",")[-1])
            if file_name:
                filename = '{}.{}'.format(file_name, file_format)
            else:
                filename = '{}_{}.{}'.format(
                    time_to_utcdate(
                        time_stamp=time.time(),
                        tformat="%Y%m%d%H%M%S"),
                    uuid1(),
                    file_format)

            # 本地服务器
            if prefix:
                filename = "{}{}".format(prefix, filename)

            # 文件保存的绝对路径
            save_file_path = "{}/{}/{}".format(
                STATIC_PATH, get_config(
                    "upload", "SAVE_DIR"), filename).replace(
                "//", "/")

            # 文件保存到本地服务器端
            save_dir = os.path.split(save_file_path)[0]
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            with open(save_file_path, 'wb') as file_w:
                file_w.write(imgdata)

            # 检测文件储存插件
            data = plugin_manager.call_plug(hook_name="file_storage",
                                            action="upload",
                                            localfile_path=save_file_path,
                                            filename=filename)
            if data != "__no_plugin__":
                # 上传后删除本地文件
                local_file_del(save_file_path)
                key = data
            else:
                key = {
                    "key": filename,
                    "bucket_name": None,
                    "d": None,
                    "type": "local"}
        else:
            key = None

        keys.append(key)
    call_file_detection.apply_async(
        kwargs={
            "files_file_url_obj": keys
        }
    )
    return keys


def upload_file(
        file=None,
        prefix="",
        file_name=None,
        file_format=None,
        fetch_url=False,
        tailoring=None):
    """
    文件保存
    :param file, 上传文件对象
    :param prefix: 给文件名加前缀, 如果prefix中有"/"，则系统也会自动根据/来建目录
    :param file_name:如果file_name是这样的post-img/xxxx-xxx-xxx.jpg，则系统也会自动根据/来建目录
    :param file_format:文件格式,如:png
    :param tailoring:不建议使用此参数建议再客户端处理完上传
    :return:
    """

    # 如果自定义名字
    if file_name:
        filename = '{}.{}'.format(file_name, file_format)
    else:
        filename = '{}-{}.{}'.format(
            time_to_utcdate(
                time_stamp=time.time()),
            uuid1(),
            file_format)

    # 本地服务器
    if prefix:
        filename = "{}{}".format(prefix, filename)

    # 文件保存的绝对路径
    save_file_path = "{}/{}/{}".format(STATIC_PATH,
                                       get_config("upload",
                                                  "SAVE_DIR"),
                                       filename).replace("//",
                                                         "/")

    # 文件保存到本地服务器端
    save_dir = os.path.split(save_file_path)[0]
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 文件保存到本地服务器端
    if fetch_url:
        urllib.request.urlretrieve(fetch_url, save_file_path)
    elif file:
        file.save(save_file_path)
        if tailoring:
            # 裁剪图片
            try:
                im = Image.open(save_file_path)
                im = im.rotate(tailoring['rotate'])
                region = im.crop(
                    (tailoring["x"],
                     tailoring["y"],
                        tailoring["x"] +
                        tailoring["width"],
                        tailoring["y"] +
                        tailoring["height"]))
                region.save(save_file_path)
            except BaseException:
                pass

        # 检测文件储存插件
        data = plugin_manager.call_plug(hook_name="file_storage",
                                        action="upload",
                                        localfile_path=save_file_path,
                                        filename=filename)
        if data != "__no_plugin__":
            # 上传后删除本地文件
            local_file_del(save_file_path)
            result = data
        else:
            result = {
                "key": filename,
                "bucket_name": None,
                "d": None,
                "type": "local"}

        return result


def copy_file(
        from_file_url_obj=None,
        from_path=None,
        replica_prefix="",
        replica_file_name=None,
        replica_file_format=None):
    """
    文件复制,同一个区域的文件才可以复制
    :param file_url_obj:和from_path二选1
    :param from_path:
    :param replica_prefix:
    :param replica_file_name:
    :param replica_file_format:
    :return:
    """

    # 如果自定义名字
    if replica_file_name:
        filename = '{}.{}'.format(replica_file_name, replica_file_format)
    else:
        filename = '{}-{}.{}'.format(
            time_to_utcdate(
                time_stamp=time.time()),
            uuid1(),
            replica_file_format)

    if replica_prefix:
        filename = "{}{}".format(replica_prefix, filename)

    filename = filename.replace("//", "/")
    if from_file_url_obj:
        if from_file_url_obj['type'] == "local":
            # 是复制本地图片
            from_local_path = get_localfile_path(from_file_url_obj)
            # 文件保存的绝对路径
            save_file_path = "{}/{}/{}".format(
                STATIC_PATH, get_config(
                    "upload", "SAVE_DIR"), filename).replace(
                "//", "/")

            # 文件保存到本地服务器端
            save_dir = os.path.split(save_file_path)[0]
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            shutil.copyfile(from_local_path, save_file_path)
            result = {
                "key": filename,
                "bucket_name": None,
                "d": None,
                "type": "local"}
            return result

        else:
            # 检图床插件
            data = plugin_manager.call_plug(hook_name="file_storage",
                                            action="copy_file",
                                            file_url_obj=from_file_url_obj,
                                            filename=filename
                                            )
            if data == "__no_plugin__":
                return None
            else:
                return data
    elif from_path:
        # 检图床插件
        data = plugin_manager.call_plug(hook_name="file_storage",
                                        action="upload",
                                        localfile_path=from_path,
                                        filename=filename,
                                        )

        if data == "__no_plugin__":
            # 文件保存的绝对路径
            save_file_path = "{}/{}/{}".format(
                STATIC_PATH, get_config(
                    "upload", "SAVE_DIR"), filename).replace(
                "//", "/")

            # 文件保存到本地服务器端
            save_dir = os.path.split(save_file_path)[0]
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            shutil.copyfile(from_path, save_file_path)
            result = {
                "key": filename,
                "bucket_name": None,
                "d": None,
                "type": "local"}
            return result
        else:
            return data


def file_del(file_url_obj):
    """
    需要提供一个路径字典
    :param file_url_obj:
    :return:
    """

    # 检测插件
    data = plugin_manager.call_plug(hook_name="file_storage",
                                    action="delete",
                                    file_url_obj=file_url_obj)
    if data == "__no_plugin__":

        path = get_localfile_path(file_url_obj=file_url_obj)
        return local_file_del(path=path)


def local_file_del(path, expiration_time=None):
    """
    删除服务器端本地图片,可以给定url删除,也可以的给定过期时间
    :param path:
    :param expiration_time:
    :return:
    """

    if path and not expiration_time:
        # 按路径删除服务器临时文件
        file_split = os.path.splitext(path)
        if os.path.exists(path):
            os.remove(path)
            # 删除比例缩放图
            for f in glob.glob(os.path.join(
                    "{}_w*_h*{}".format(file_split[0], file_split[1]))):
                os.remove(f)
            return True
        else:
            return False

    elif expiration_time:
        # 按文件名称的时间遍历删除
        rm_file_list = []
        if not os.path.exists(path):
            return False

        list_file = os.listdir(path)
        if list_file:
            for file in os.listdir(path):
                try:
                    if time.time() - float(file.split("__")
                                           [0]) > expiration_time:
                        # 已过期
                        file_path = os.path.join("{}/{}".format(path, file))
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            rm_file_list.append("{}/{}".format(path, file))
                except BaseException:
                    pass
            return True
        else:
            return False


def file_rename(file_url_obj, new_filename):
    """
    需要提供一个本系统定义的文件字典
    :param filedict:
    :return:
    """

    # 检测插件
    data = plugin_manager.call_plug(hook_name="file_storage",
                                    action="delete",
                                    file_url_obj=file_url_obj,
                                    new_filename=new_filename)

    if data == "__no_plugin__":

        path = get_localfile_path(file_url_obj=file_url_obj)
        file_format = os.path.splitext(path)[-1]
        new_path = "{}/{}{}".format(os.path.split(path)[0],
                                    os.path.split(path)[1],
                                    file_format)
        os.rename(path, new_path)
        return True
    else:
        return data


@celery.task(base=QueueOnce, once={'graceful': True})
def call_file_detection(files_file_url_obj):
    """
    调用文件检查
    :param file_urls:
    :return:
    """

    for file_url_obj in files_file_url_obj:
        url = get_file_url(file_url_obj)
        r = content_inspection_image(url=url)
        if r['score'] >= get_config(
            "content_inspection",
                "ALLEGED_ILLEGAL_SCORE"):
            # 违规
            file_del(file_url_obj)
            replica_file_path_list = os.path.splitext(file_url_obj["key"])
            copy_file(from_path=VIOLATION_IMG_PATH,
                      replica_file_name=replica_file_path_list[0],
                      replica_file_format=replica_file_path_list[-1].lstrip("."))


def allowed_file(filename):
    """
    图片格式后缀验证
    :param filename:
    :return:
    """

    return os.path.splitext(filename)[1].strip(
        ".").lower() in get_config("upload", "UP_ALLOWED_EXTENSIONS")
