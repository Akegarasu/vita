#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2020/03/14 12:44
# @Author : Allen Woo
import sys
from signal import signal, SIGCHLD, SIG_IGN
from pymongo.errors import OperationFailure
from apps.configs.db_config import DB_CONFIG
from apps.core.db.config_mdb import DatabaseConfig
from apps.core.db.mongodb import MyMongo
from apps.develop_run_options import start_info_print
from apps.app import app
from apps.brand_info import start_info


def init_before_startup(is_debug, csrf_enabled):
    """
    启动前初始化相关数据
    :param is_debug:
    :param csrf_enabled:
    :return:
    """
    start_info()
    start_info_print("\033[1;36m osroom staring...\033[0m")

    # 网站还未启动的时候, 临时连接数据库, 更新collections & 系统配置
    from apps.core.utils.update_sys_data import update_mdb_collections, init_datas, \
        compatible_processing
    database = DatabaseConfig()
    mdbs = {}

    # 创建局部临时数据库对象
    for k, mdb_acc in DB_CONFIG["mongodb"].items():
        mdbs[k] = MyMongo()

    # 初始化2次，第一次初始化是为了更新mdb的collections
    # 如果第一次更新后存在新的collections，需要再次初始化数据库供其他程序使用
    db_init = 2
    while db_init:
        try:
            for name, mdb in mdbs.items():
                if db_init == 1:
                    mdb.close()
                if name not in ["sys", "user", "web"]:
                    msg = "[Error]: 由v1.x.x更新到v2.x.x需要请更新你的数据库配置文件apps/configs/db_config.py." \
                          "请参考同目录下的db_config_sample.py"
                    start_info_print('\033[31m{}\033[0m'.format(msg))
                    sys.exit()
                mdb.init_app(
                    config_prefix=name.upper(),
                    db_config=database.__dict__["{}_URI".format(name.upper())]
                )

        except OperationFailure as e:

            msg = "\n[Mongodb] *{}\nMongodb validation failure, the user name, " \
                  "password mistake or database configuration errors.\n" \
                  "Tip: to open database authentication configuration".format(e)
            start_info_print('\033[31m{}\033[0m'.format(msg))

            sys.exit(-1)
        if db_init == 2 and is_debug:
            # 更新数据库文档表
            start_info_print(" * Check or update the database collection")
            update_mdb_collections(mdbs=mdbs)
        else:
            # 未更新数据库coll，无需二次初始化数据库，直接break
            break
        db_init -= 1

    if not is_debug:
        # 更新配置文件
        from apps.core.flask.update_config_file import update_config_file
        start_info_print(" * Update and sync config.py")
        r = update_config_file(mdbs=mdbs)
        if not r:
            start_info_print("[Error] Update profile error, check log sys_start.log")
            sys.exit(-1)
    else:
        msgs = " * The following services need to be run in a non-debugger state.\n" \
               "   Including the following services:- Automatic update of Mongodb collections.\n" \
               "   - Automatic update of website routing rights control.\n" \
               "   - Automatically update and merge system configuration.\n\n"

        warning_msg = "\033[03m   " \
                      "If the program runs incorrectly because the above configuration \n" \
                      "   is not updated, you need to remove the debugger running program \n" \
                      "   first to implement the update. After that, you can continue to run \n" \
                      "   the program under the debugger."
        start_info_print('\033[33m{}{}\033[0m'.format(msgs, warning_msg))

    # 调用兼容程序step 1
    compatible_processing(mdbs=mdbs, stage=1)

    # 调用初始化数据
    init_datas(mdbs=mdbs)
    for mdb in mdbs.values():
        mdb.close()

    # 核心程序初始化+模块加载
    from apps.core.flask.module_import import module_import
    from apps.init_core_module import init_core_module
    from apps.configs.sys_config import MODULES
    init_core_module(
        app,
        csrf_enabled=csrf_enabled,
        is_debug=is_debug
    )
    module_import(MODULES)

    # 调用兼容程序step 2
    from apps.app import mdbs
    compatible_processing(mdbs=mdbs, stage=2)

    if not is_debug:
        start_info_print(
            " * Signal:(SIGCHLD, SIG_IGN)."
            "Prevent child processes from becoming [Defunct processes]."
            "(Do not need to comment out)")
        signal(SIGCHLD, SIG_IGN)
        start_info_print(" * Started successfully")
    else:
        start_info_print(" * Debugger: Started successfully")
