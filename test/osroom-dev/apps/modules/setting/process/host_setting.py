#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from bson import ObjectId
from flask import request
from flask_babel import gettext
from apps.app import mdbs
import regex as re
from apps.core.flask.reqparse import arg_verify
from apps.core.utils.get_config import get_config
from apps.utils.format.obj_format import json_to_pyseq
from apps.utils.pyssh.pyssh import audit_host_info, MySSH


def get_sys_host():

    ip = request.argget.all('host_ip')
    host = mdbs["sys"].db.sys_host.find_one({"host_info.local_ip": ip})
    host["_id"] = str(host["_id"])
    if get_config("system", "KEY_HIDING") and "password" in host["host_info"] and\
            host["host_info"]["password"]:
        host["host_info"]["password"] = "Has been hidden"

    data = {"host": host}
    if get_config("system", "KEY_HIDING"):
        data["msg_type"] = "w"
        data["msg"] = gettext(
            "The KEY_HIDING switch in the system configuration has been enabled."
            " The value of the password type has been replaced.")

    return data


def sys_host_edit():

    ip = request.argget.all('host_ip')
    port = int(request.argget.all('host_port', 22))
    username = request.argget.all('username')
    password = request.argget.all('password')
    cmd = request.argget.all('cmd', "")
    msg = None
    s, r = arg_verify(reqargs=[("IP", ip), (gettext(
        "username"), username), (gettext("password"), password)], required=True)
    if not s:
        return r
    if msg:
        data = {"msg": msg, "msg_type": "w", "custom_status": 422}
    else:
        r = mdbs["sys"].db.sys_host.update_one({"host_info.local_ip": ip},
                                           {"$set": {"host_info.port": port,
                                                     "host_info.username": username,
                                                     "host_info.password": password,
                                                     "host_info.local_ip"
                                                     "cmd": cmd}})

        if r.modified_count:
            data = {
                "msg": gettext("The update is successful"),
                "msg_type": "s",
                "custom_status": 201}
        else:
            data = {
                "msg": gettext("No changes"),
                "msg_type": "w",
                "custom_status": 201}
    return data


def sys_host_delete():

    ids = json_to_pyseq(request.argget.all('ids', []))

    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)
    r = mdbs["sys"].db.sys_host.delete_many({"_id":{"$in":ids}})
    if r.deleted_count:
        data = {"msg": gettext("Successfully deleted {} host information").format(
            r.deleted_count), "msg_type": "s", "custom_status": 204}
    else:
        data = {
            "msg": gettext("Failed to delete"),
            "msg_type": "w",
            "custom_status": 400}
    return data


def sys_host_exec_cmd():

    ip = request.argget.all('host_ip')
    host = mdbs["sys"].db.sys_host.find_one({"host_info.local_ip": ip})
    exec_cmd = request.argget.all('cmd', "")
    if host:
        host_info = host["host_info"]
        s, v = audit_host_info(host_info)
        if not s:
            return v
        else:
            try:
                ssh = MySSH(host=ip, port=host_info["port"],
                            username=host_info["username"],
                            password=host_info["password"])
            except BaseException as e:
                data = {"msg": gettext("[{}] {}").format(ip, str(e)),
                        "msg_type": "e", "custom_status": 400}
                return data

            if not ssh:
                data = {
                    "msg": gettext("Connection host[{}] failed,Check the host Settings").format(ip),
                    "msg_type": "e",
                    "custom_status": 400}
                return data
        result = []
        if not exec_cmd and "cmd" in host:
            exec_cmd = host["cmd"]

        for cmd in exec_cmd.split("\n"):
            cmd = cmd.strip()
            if re.search(r"^#.*", cmd):
                continue

            if re.search(
                    r"^sudo\s*.*",
                    cmd) or re.search(
                    r".*\s+sudo\s+.*",
                    cmd):
                result.append(
                    [gettext('[Warning]: "sudo" command go to the server')])
            elif re.search(r"^rm\s+.*", cmd) or re.search(r".*\s+rm\s+.*", cmd):
                result.append(
                    [gettext('[Warning]: "rm" command go to the server')])
            else:
                stdin, stdout, stderr = ssh.exec_cmd("nohup {} &".format(cmd))
                result.append(stdout.read().decode().split("\n"))
        ssh.close()
        data = {"msg": gettext("Command executed {}").format(ip),
                "msg_type": "s", "custom_status": 201,
                "result": result, "cmd": exec_cmd}
    else:
        data = {"msg": gettext("There is no host {}").format(
            ip), "msg_type": "e", "custom_status": 400}

    return data


def sys_host_connect_test():

    ip = request.argget.all('host_ip')
    host = mdbs["sys"].db.sys_host.find_one({"host_info.local_ip": ip})

    if host:
        host_info = host["host_info"]
        s, v = audit_host_info(host_info)
        if not s:
            return v
        else:
            try:
                ssh = MySSH(host=ip, port=host_info["port"],
                            username=host_info["username"],
                            password=host_info["password"])
            except BaseException as e:
                data = {"msg": gettext("[{}] {}").format(ip, str(e)),
                        "msg_type": "e", "custom_status": 400}
                return data
            if not ssh:
                data = {
                    "msg": gettext("Connection host[{}] failed").format(ip),
                    "msg_type": "e",
                    "custom_status": 400}
            else:

                data = {
                    "msg": gettext("Successfully connecting server host"),
                    "msg_type": "s",
                    "custom_status": 201}
    else:
        data = {
            "msg": gettext("Host does not exist"),
            "msg_type": "e",
            "custom_status": 400}
    return data
