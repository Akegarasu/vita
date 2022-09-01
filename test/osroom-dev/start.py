#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os
import sys
from apps.configs.db_config import DB_CONFIG
from apps.core.db.config_mdb import DatabaseConfig
from apps.core.db.mongodb import MyMongo
from apps.core.utils.sys_tool import init_admin_user
from apps.core.utils.update_sys_data import update_mdb_collections, \
    init_datas, update_mdbcolls_json_file
from apps.develop_run_options import parameter_processing
from apps.app import app
from apps.init_before_startup import init_before_startup

# osroom启动前初始化入口
no_need_to_init_ops = ["run-osroom", "--help", "routes", "shell"]
sys_argv = list(sys.argv)
if not len(set(sys_argv) & set(no_need_to_init_ops)):
    if "run" in sys_argv and "uwsgi" not in sys_argv:
        # 开发环境下
        other_ops = parameter_processing(sys_argv=sys_argv, op="read")
        is_debug = other_ops.get("is_debug", True)
        csrf_enabled = other_ops.get("csrf_enabled", True)
    elif not os.environ.get('FLASK_ENV'):
        # 生产环境下
        is_debug = False
        csrf_enabled = True
    else:
        sys.exit(-1)

    init_before_startup(is_debug=is_debug, csrf_enabled=csrf_enabled)


def temp_init_mdb():
    mdbs = {}
    database = DatabaseConfig()
    for k in DB_CONFIG["mongodb"].keys():
        mdbs[k] = MyMongo()
        mdbs[k].init_app(
            config_prefix=k.upper(),
            db_config=database.__dict__["{}_URI".format(k.upper())]
        )
    return mdbs


@app.cli.command()
def add_user():
    """
    CN:初始化root用户或修改存在root用户密码
    EN: Initialize a root user or modify an existing root user password
    :return:
    """
    # 创建局部临时数据库对象
    mdbs = temp_init_mdb()
    update_mdb_collections(mdbs=mdbs)
    init_datas(mdbs=mdbs, init_theme=False)
    init_admin_user(mdbs=mdbs)


@app.cli.command()
def dbtable_to_file():
    """
    CN: 更新mongodb的collections基本信息到json文件中保存
    EN: Update the basic collections information of mongodb and save it in the json file
    """
    mdbs = temp_init_mdb()
    update_mdbcolls_json_file(mdbs=mdbs)
