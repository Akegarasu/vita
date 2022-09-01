#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from importlib import import_module, reload
import os
import sys
import time
import shutil
import re
import yaml
from flask_babel import gettext

from apps.app import mdbs, cache
from apps.configs.sys_config import PLUG_IN_FOLDER, PLUG_IN_FOLDER_NAME, PLUG_IN_REQUIRED_CONF


class PluginManager:
    """
    插件管理
    """

    def __init__(self):
        self.init_app()

    def init_app(self):

        self.__registered_plugin = {}
        self.__registered_plugin_name_list = []
        self.plugin_path = PLUG_IN_FOLDER
        self.current_time = time.time()
        self.load_all_plugin()

    def load_plugin(self, plugin_name, is_import=False):
        """
        加载插件 import
        :param plugin_name:
        :return:
        """

        plug_path = os.path.join(self.plugin_path, plugin_name)
        s, r = verify_plugin(plug_path)
        if not s:
            # 标记插件为出错插件
            mdbs["sys"].dbs["plugin"].update_one(
                {
                    "plugin_name": plugin_name,
                    "update_time": {"$lt": self.current_time}},
                {
                    "$set": {
                        "error": r,
                        "installed_time": self.current_time,
                        "update_time": self.current_time,
                        "active": 0,
                        "require_package_install_result": []
                    }
                },
                upsert=True)
            return s, r

        # 查看是否有需求文件
        if os.path.exists(os.path.join(plug_path, "requirements.txt")):
            requirements_exist = True
        else:
            requirements_exist = False

        # 读取yaml配置
        fpath = os.path.join(plug_path, "conf.yaml")
        with open(fpath) as rf:
            # 读取插件配置文件
            plug_conf = yaml.safe_load(rf)
            hook_name = plug_conf["hook_name"]
            module = None
            current_plug = mdbs["sys"].dbs["plugin"].find_one(
                {"plugin_name": plugin_name})

            freed = False
            # 如果插件存在, 并标记为删除，那就删除插件文件
            if current_plug and "is_deleted" in current_plug and current_plug["is_deleted"]:
                try:
                    shutil.rmtree(plug_path)
                except BaseException:
                    pass
                freed = True

            if is_import or (current_plug and current_plug["error"]):
                # 需要导入插件模块或者插件模块之前鉴定有错误
                startup_file_name = plug_conf["startup_file_name"]
                plug_main_file_path = os.path.join(
                    plug_path, startup_file_name)
                if os.path.exists(plug_main_file_path):
                    module_path = "apps.{}.{}.{}".format(
                        PLUG_IN_FOLDER_NAME, plugin_name, startup_file_name[:-3])
                    try:
                        if module_path in sys.modules:
                            # 如果之前已加载
                            module = reload(sys.modules[module_path])
                        else:
                            module = import_module(module_path)
                    except BaseException as e:
                        # 标记插件为出错插件
                        mdbs["sys"].dbs["plugin"].update_one(
                            {
                                "plugin_name": plugin_name,
                                "update_time": {
                                    "$lt": self.current_time}},
                            {
                                "$set": {
                                    "error": str(e),
                                    "update_time": self.current_time,
                                    "active": 0,
                                    "requirements_exist": requirements_exist,
                                    "require_package_install_result": []}},
                            upsert=True)

                        return False, str(e)

                else:
                    return False, "{} {}".format(
                        gettext("Plugin startup file does not exist"), plug_main_file_path)

            # 需要更新的数据
            plug_conf["plugin_name"] = plugin_name
            plug_conf["update_time"] = self.current_time
            plug_conf["error"] = 0
            plug_conf["requirements_exist"] = requirements_exist
            # 检测当前插件安装情况
            if current_plug:

                # 如果插件未激活
                if not current_plug["active"]:
                    freed = True

                if freed:
                    # 释放实例对象
                    self.unregister_plugin(plugin_name)

                # 更新插件信息到数据库
                mdbs["sys"].dbs["plugin"].update_one(
                    {
                        "plugin_name": plugin_name,
                        "update_time": {
                            "$lt": self.current_time}
                    },
                    {"$set": plug_conf})

            else:
                # 插件不存在
                plug_conf["active"] = 0
                plug_conf["is_deleted"] = 0
                plug_conf["installed_time"] = self.current_time
                mdbs["sys"].dbs["plugin"].insert_one(plug_conf)

            # 清理遗留缓存
            cache.delete_autokey(
                fun="get_plugin_info",
                db_type="redis",
                hook_name=hook_name)
            return True, {"module": module,
                          "hook_name": hook_name, "plugin_name": plugin_name}

    def load_all_plugin(self):
        """
        加载全部插件
        :return:
        """
        # 遍历插件目录
        plugins = os.listdir(self.plugin_path)
        self.current_time = time.time()
        for f in plugins:
            if f.startswith("__"):
                continue
            fpath = os.path.join(self.plugin_path, f)
            if os.path.isdir(fpath):
                # 加载全部插件的时候不需要import到运行程序中, register_plugin要用时发现没有导入会自动导入
                self.load_plugin(f)

        # 清理已不存在插件的信息
        mdbs["sys"].dbs["plugin"].delete_many(
            {"update_time": {"$lt": self.current_time}})

    def call_plug(self, hook_name, *args, **kwargs):
        """
        通过hook_name调用已注册插件
        :param hook_name:
        :return:
        """
        data = "__no_plugin__"
        # 获取一个已激活插件
        activated_plugin = get_plugin_info(hook_name=hook_name)
        if activated_plugin:
            # 如果存在，则查看名为hook_name的插件是否已经注册
            plug = self.__registered_plugin.get(hook_name)
            if plug and plug["plugin_name"] == activated_plugin["plugin_name"]:
                # 如果当前激活的插件已经注册，直接调用
                main_func = plug["module"].main
            else:
                # 如果当前主机系统没有当前激活注册，则注册插件后再调用
                s = self.register_plugin(activated_plugin["plugin_name"])
                if s:
                    plug = self.__registered_plugin.get(hook_name)
                    main_func = plug["module"].main
                else:
                    return data
            # 执行插件
            data = main_func(*args, **kwargs)
        return data

    def register_plugin(self, plugin_name):
        """
        注册插件
        :param plugin_name:
        :return:
        """
        self.current_time = time.time()
        s, r = self.load_plugin(plugin_name, is_import=True)
        if s:
            self.__registered_plugin[r["hook_name"]] = r
            self.__registered_plugin_name_list.append(plugin_name)
            return True
        return False

    def unregister_plugin(self, plugin_name):
        """
        注销插件, 只能
        :param pLuginName:
        :return:
        """
        if plugin_name in self.__registered_plugin_name_list:
            for k, v in self.__registered_plugin.items():
                if plugin_name == v["plugin_name"]:
                    del v["module"]
                    del self.__registered_plugin[k]
                    return True
        return False


def verify_plugin(plugin_path):

    conf_path = os.path.join(plugin_path, "conf.yaml")
    if os.path.exists(conf_path) and os.path.isfile(conf_path):
        with open(conf_path) as rf:
            plug_conf = yaml.safe_load(rf)
            req_conf = PLUG_IN_REQUIRED_CONF.copy()
            req_conf = list(set(req_conf).difference(set(plug_conf.keys())))
            if req_conf:
                data = gettext('Configuration file "conf.yaml" but few parameters "{}"').format(
                    ", ".join(req_conf))
                return False, data
            elif not os.path.exists(os.path.join(plugin_path, plug_conf["startup_file_name"])):
                data = gettext('Missing startup file in plugin package')
                return False, data

        startup_file = os.path.join(
            plugin_path, plug_conf["startup_file_name"])
        func_main_exists = False
        with open(startup_file) as rf:
            for line in rf.readlines():
                if re.search(r"def\s+main\(.+\)\s*:$", line.strip()):
                    func_main_exists = True
                    break
        if func_main_exists:
            data = gettext("Plugin installed successfully")
            return True, data
        else:
            data = gettext('Missing plugin main function(execution function)')
            return False, data

    else:
        data = "The plugin of the upload is incorrect," \
            "the configuration file(conf.yaml) does not exist"
        return False, data


@cache.cached(timeout=86400 * 7, key_base64=False, db_type="redis")
def get_plugin_info(hook_name):
    """
    获取插件信息
    :hook_name url:
    :return:
    """
    value = mdbs["sys"].dbs["plugin"].find_one(
        {
            "hook_name": hook_name,
            "active": {"$in": [1, True]}},
        {
            "_id": 0
        })
    return value


plugin_manager = PluginManager()
