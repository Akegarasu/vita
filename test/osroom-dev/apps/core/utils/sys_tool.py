#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import json
import time
import os
import sys
import subprocess
from getpass import getpass
from copy import deepcopy
import requests
from apps.configs.sys_config import PROJECT_PATH, SUPER_PER, LOG_PATH
from apps.utils.format.time_format import time_to_utcdate


def copy_config_to_sample():
    """
    复制db_account.py到db_account_sample,　并把密码替换掉，以免暴露到网上
    """

    from apps.configs.db_config import DB_CONFIG

    # 复制db_config.py 到　db_config_sample.py
    local_config = deepcopy(DB_CONFIG)
    for v in local_config.values():
        if isinstance(v, dict):
            for k1, v1 in v.items():
                if k1 == "password":
                    v[k1] = "<Your password>"
                elif isinstance(v1, dict):
                    for k2, v2 in v1.items():
                        if k2 == "password":
                            v1[k2] = "<Your password>"

    # 复制配置文件为sample配置文件
    info = """# -*-coding:utf-8-*-\n__author__ = "Allen Woo"\n"""
    temp_conf = str(json.dumps(local_config, indent=4, ensure_ascii=False))
    wf = open("{}/apps/configs/db_config_sample.py".format(PROJECT_PATH), "wb")
    wf.write(bytes(info, "utf-8"))
    wf.write(bytes("DB_CONFIG = ", "utf-8"))
    wf.write(
        bytes(
            temp_conf.replace(
                "false",
                "False").replace(
                "true",
                "True").replace(
                    "null",
                    "None"),
            "utf-8"))
    wf.close()
    print("It has been updated db_config_sample.py")


def init_admin_user(mdbs):
    """
    初始化root用户角色, 管理员, 管理员基本资料
    :return:
    """
    from werkzeug.security import generate_password_hash
    from apps.modules.user.models.user import user_model
    from apps.modules.user.process.get_or_update_user import \
        get_one_user_mfilter, update_one_user, insert_one_user

    print('\nInit root user')
    # 初始化角色
    root_per = SUPER_PER
    role_root = mdbs["user"].db.role.find_one({"permissions": root_per})
    if not role_root:
        print(" * Create root role...")
        r = mdbs["user"].db.role.insert_one(
            {
                "name": "Root",
                "default": 0,
                "permissions": root_per,
                "instructions": 'Root'
            }
        )

        if r.inserted_id:
            print("Create root user role successfully")
        else:
            print("\033[31m[Error] Failed to create superuser role\033[0m")
            sys.exit(-1)

        root_id = r.inserted_id
    else:
        root_id = role_root['_id']

    root_user = mdbs["user"].dbs["user"].find_one(
        {"role_id": str(root_id)},
        {
            "username": 1,
            "email": 1
        }
    )
    password = "12345678"
    if root_user:
        ch = input("\033[33m\n Root user already exists, need to update its password?[Y/n]\033[0m")
        if ch != "Y":
            print("End")
            sys.exit()
        is_continue = False
        while not is_continue:
            password = getpass("Input password(Password at least 8 characters):")
            if len(password) < 8:
                print("\033[33m[Warning]: {}The password is at least 8 characters\033[0m\n")
            else:
                break
        password_hash = generate_password_hash(password)
        update_one_user(
            user_id=str(root_user["_id"]),
            updata={
                "$set": {
                    "password": password_hash
                }
            })
        username = root_user["username"]
        email = root_user["email"]

    else:
        is_continue = False
        username = "osrRoot"
        email = input("Input email:")
        while not is_continue:
            password = getpass("Input password(Password at least 8 characters):")
            if len(password) < 8:
                print("\033[33m[Warning]: {}The password is at least 8 characters\033[0m\n")
            else:
                break
        try:
            mdbs["user"].dbs.create_collection("role")
            print(' * Created role collection')
        except BaseException:
            pass
        try:
            mdbs["user"].dbs.create_collection("user")
            print(' * Created user collection')
        except BaseException:
            pass

        password_hash = generate_password_hash(password)
        user = get_one_user_mfilter(email=email, op="or")
        if user:
            update_one_user(
                user_id=str(user["_id"]),
                updata={
                    "$set": {
                        "password": password_hash,
                        "role_id": str(root_id)
                    }
                }
            )
            username = user["username"]
            print("\033[33m\n * This user already exists, updated password and role.\033[0m")
        else:
            print(' * Create root user...')
            user = user_model(
                username=username,
                email=email,
                password=password,
                custom_domain=-1,
                role_id=str(root_id),
                active=True)
            r = insert_one_user(updata=user)
            if r.inserted_id:
                print(" * Create a root user successfully")
            else:
                print("\033[31m * [Error] Failed to create a root user\033[0m")
                sys.exit(-1)

    # To create the average user role
    average_user = mdbs["user"].db.role.find_one({"permissions": 1})
    if not average_user:
        print(" * Create the average user role...")
        r = mdbs["user"].db.role.insert_one({
            "name": "User",
            "default": 1,
            "permissions": 1,
            "instructions": 'The average user',
        })
        if r.inserted_id:
            print(" * Create a generic role successfully")
        else:
            print(" * Failed to create a generic role")

    role = mdbs["user"].db.role.find_one({"_id": root_id})
    hidden_password = "{}****{}".format(password[0:2], password[6:])
    print('\nThe basic information is as follows')
    print('Username: {}\nEmail: {}\nUser role: {}\nPassword: \033[33m{}\033[0m'.format(
        username, email, role["name"], hidden_password))
    print('End')
    sys.exit()


def update_pylib(venv_path=True, latest=False, is_yes=False):
    """
    更新python环境库
    :param input_venv_path:
    :return:
    """
    if venv_path == "default" and not is_yes:
        input_str = input(
            "Already running this script in your project python virtual environment?(yes/no):\n"
        )
        if input_str.upper() == "YES":
            venv_path = None
        else:
            venv_path = input("Enter a virtual environment:\n")
    elif venv_path == "null":
        venv_path = None

    if venv_path:
        if os.path.exists("{}/bin/activate".format(venv_path)):
            venv = ". {}/bin/activate && ".format(venv_path)
        else:
            venv = ". {}/bin/activate && ".format(sys.prefix)
    else:
        venv = ""

    # 检查网络情况
    is_time_out = False
    try:
        requests.get("https://www.bing.com/", timeout=10)
    except Exception as e:
        is_time_out = True
        print(e)
    if not is_time_out:
        print(" * Update pip...")
        s, r = subprocess.getstatusoutput("{}pip3 install -U pip".format(venv))
        print("   {}".format(r))
    else:
        print(" \033[31m ** Timeout for connecting to external network\033[0m")
    s, r = subprocess.getstatusoutput("{}pip3 freeze".format(venv))
    venv_exist_libs = r.split()
    req_txt_filepath = "{}/requirements.txt".format(PROJECT_PATH)
    with open(req_txt_filepath) as rf:
        # req_file_libs
        req_file_libs = rf.read().split()

    # 查找需要安装的包
    if latest:
        need_install_libs = req_file_libs[:]
    else:
        need_install_libs = list(set(req_file_libs).difference(set(venv_exist_libs)))

    for pylib in need_install_libs[:]:
        if "==" not in pylib:
            need_install_libs.remove(pylib)
    print(" * Libraries that need to be installed: {}".format(len(need_install_libs)))
    print(" ".join(need_install_libs))

    # Install
    install_failed = []
    installed = []
    if not is_time_out:
        for sf in need_install_libs:
            if latest:
                sf = sf.split("==")[0]
            shcmd = "{}pip3 install -U {}".format(venv, sf)
            print(shcmd)
            s, r = subprocess.getstatusoutput(shcmd)
            if s:
                install_failed.append(sf)
                print("\033[31m Failed\033[0m")
            else:
                installed.append(sf)
                print(" Succeeded")
        # Try again
        for sf in install_failed:
            s, r = subprocess.getstatusoutput(
                "{}pip3 install -U {}".format(venv, sf))
            if not s:
                install_failed.remove(sf)
                installed.append(sf)

    # 查找需要卸载的软件包
    s, r = subprocess.getstatusoutput("{}pip3 freeze".format(venv))
    venv_libs = r.split()
    temp_venv_libs = []
    for sf in venv_libs:
        if "==" in sf:
            temp_venv_libs.append(sf.split("==")[0])
    if latest:
        unwanted_libs = list(set(temp_venv_libs).difference(set(installed)))
    else:
        temp_req_file_libs = []
        for sf in req_file_libs:
            if "==" in sf:
                temp_req_file_libs.append(sf.split("==")[0])
        unwanted_libs = list(set(temp_venv_libs).difference(set(temp_req_file_libs)))
    for sf in unwanted_libs[:]:
        if "==" not in sf:
            unwanted_libs.remove(sf)

    print(" \n*[Succeeded] Libs: {}".format(len(installed)))
    print(" ".join(installed))
    print(" \033[31m\n* [Failed] Libs, please manually install: {}".format(len(install_failed)))
    print(" ".join(install_failed))
    print(" \n* Now don't need python library: {}".format(len(unwanted_libs)))
    print(" ".join(unwanted_libs))
    print("\033[0m")
    if latest:
        with open(req_txt_filepath, "w") as wf:
            wf.write("\n".join(venv_libs))
        update_log = "{}/pylibs_update.log".format(
            LOG_PATH
        )
        with open(update_log, "w") as wf:
            lines = [
                "Python libraries and version numbers before{}\n".format(
                    time_to_utcdate(time.time(), "%Y/%m/%d %H:%M:%S")
                ),
                "\n".join(req_file_libs)
            ]
            wf.writelines(lines)
        msg = " * The library that installed the latest version has been opened,\n" \
              " and the requirement file has been rewritten.\n" \
              " To view the previous version, please check the file:\n {}\n".format(update_log)
        print(msg)
