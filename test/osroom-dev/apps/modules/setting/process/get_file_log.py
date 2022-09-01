#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import os
from flask import request
from flask_babel import gettext
from apps.configs.sys_config import PROJECT_PATH
from apps.utils.paging.paging import datas_paging
from apps.utils.pyssh.pyssh import MySSH, audit_host_info
from apps.app import mdbs


def sys_log():

    name = request.argget.all('name')
    ip = request.argget.all('ip')
    page = int(request.argget.all('page', 1))

    host = mdbs["sys"].db.sys_host.find_one({"host_info.local_ip": ip})
    if host:
        host_info = host["host_info"]
        s, v = audit_host_info(host_info)
        if not s:
            return v
        else:
            ssh = MySSH(ip, port=host_info["port"],
                        username=host_info["username"],
                        password=host_info["password"])
            if not ssh:
                data = {
                    "msg": gettext("Connection host[{}] failed,Check the host Settings").format(ip),
                    "msg_type": "e",
                    "custom_status": 400}
                return data
        sftp = ssh.client.open_sftp()
        remote_file = "{}/logs/{}".format(PROJECT_PATH, name)
        local_temp_log_dir = '{}/logs/remote_file'.format(PROJECT_PATH)
        if not os.path.exists(local_temp_log_dir):
            os.makedirs(local_temp_log_dir)

        local_file = '{}/{}_{}'.format(local_temp_log_dir,
                                       ip,
                                       name)
        sftp.get(remote_file, local_file)
        ssh.close()

        pre = 50
        rf = open(local_file)
        count = 0
        while True:
            buffer = rf.read(8192 * 1024)
            if not buffer:
                break
            count += buffer.count('\n')
        rf.close()
        logs = []
        n = 1
        with open(local_file) as f:
            for line in f:
                if n > (page - 1) * pre:
                    logs.append(line)
                if n >= page * pre:
                    break
                n += 1
        f.close()
        logs = datas_paging(pre=pre, page_num=page, data_cnt=count, datas=logs)
        logs["datas"] = "".join(logs["datas"])
        logs["datas"] = logs["datas"].replace("\n", "<br>")
        data = {"logs": logs}
        os.remove(local_file)
    else:
        data = {"msg": gettext("There is no host {}").format(ip),
                "msg_type": "e", "custom_status": 400}
    return data
