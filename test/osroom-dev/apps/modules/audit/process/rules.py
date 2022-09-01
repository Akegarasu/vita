#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import json
from bson import ObjectId
from flask import request
from flask_babel import gettext
import time

from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import objid_to_str, json_to_pyseq
from apps.utils.paging.paging import datas_paging
from apps.app import mdbs


def audit_rules():

    data = {}
    project = request.argget.all('project', 'username')
    keyword = request.argget.all('keyword')
    page = int(request.argget.all('page', 1))
    pre = int(request.argget.all('pre', 10))
    q = {}
    if project:
        q["project"] = project
    if keyword:
        keyword = {"$regex": keyword, "$options": "$i"}
        q["$or"] = [
            {"rule": keyword}
        ]
    rules = mdbs["sys"].db.audit_rules.find(q)
    data_cnt = rules.count(True)
    rules = objid_to_str(
        list(rules.sort([("time", -1)]).skip(pre * (page - 1)).limit(pre)))
    data["Python-rules"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=rules)
    return data


def audit_rule_add():
    project = request.argget.all('project')
    rule = request.argget.all('rule')

    reqargs = [(gettext("rule"), rule), ("project", project)]
    s, r = arg_verify(reqargs=reqargs, required=True)
    if not s:
        return r
    else:
        if mdbs["sys"].db.audit_rules.find_one(
            {
                "project": project,
                "rule": rule
                }):
            data = {
                "msg": gettext("The rule already exists"),
                "msg_type": "w",
                "custom_status": 403}
        else:
            mdbs["sys"].db.audit_rules.insert_one(
                {
                    "rule": rule,
                    "project": project,
                    "time": time.time()
                })
            data = {
                "msg": gettext("Add a success"),
                "msg_type": "s",
                "custom_status": 201
            }
    return data


def audit_rule_delete():

    ids = json_to_pyseq(request.argget.all('ids', []))
    if not isinstance(ids, list):
        ids = json.loads(ids)
    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)

    r = mdbs["sys"].db.audit_rules.delete_many({"_id": {"$in": ids}})
    if r.deleted_count > 0:
        data = {"msg": gettext("Delete the success,{}").format(
            r.deleted_count), "msg_type": "s", "custom_status": 204}
    else:
        data = {
            "msg": gettext("Delete failed"),
            "msg_type": "w",
            "custom_status": 400}
    return data
