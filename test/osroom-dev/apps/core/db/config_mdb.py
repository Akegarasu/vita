#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from pymongo import ReadPreference
from apps.configs.db_config import DB_CONFIG


class DatabaseConfig:

    """
    database
    """

    def __init__(self, *args, **kwargs):
        self.mongodb()

    def mongodb(self):
        """
        MongoDB setting
        :return:
        """
        # MONGODB
        mongodbs = DB_CONFIG["mongodb"]
        for prefix, conf in mongodbs.items():

            if prefix == "sys":
                # session数据库名称, 如果选择使用mongodb做session数据库时有效
                self.session_dbname = conf["dbname"]

            # 拼接uri
            hosts = "mongodb://{username}:{password}@".format(username=conf["username"],
                                                              password=conf["password"])
            l = len(conf["host"])
            for i, chost in enumerate(conf["host"]):
                if i == (l - 1):
                    hosts = "{}{}".format(hosts, chost)
                else:
                    hosts = "{}{},".format(hosts, chost)

            hosts_uri = "%s/{}" % (hosts)

            # 其他配置
            config_prefix = prefix.upper()
            other_config = conf["config"]
            config = {
                "mongodb": hosts_uri.format(
                    conf["dbname"]),
                "db": conf["dbname"],
                "read_preference": ReadPreference.SECONDARY_PREFERRED}
            if isinstance(other_config, dict):
                for k, v in other_config.items():
                    config[k] = v
            self.__dict__["{}_URI".format(config_prefix)] = config
