#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.core.flask.reqparse import arg_verify
from apps.modules.permission.process.permission import permissions
from apps.utils.format.number import get_num_digits
from apps.utils.format.obj_format import objid_to_str, json_to_pyseq
from apps.utils.paging.paging import datas_paging
from apps.app import mdbs


def role():

    rid = request.argget.all('id').strip()
    data = {}
    data["role"] = mdbs["user"].db.role.find_one({"_id": ObjectId(rid)})
    if not data["role"]:
        data = {
            'msg': gettext("The specified role is not found"),
            'msg_type': "w",
            "custom_status": 404}
    else:
        data["role"]["_id"] = str(data["role"]["_id"])

    return data


def roles():
    data = {}
    page = int(request.argget.all('page', 1))
    pre = int(request.argget.all('pre', 10))
    rs = mdbs["user"].db.role.find({})
    data_cnt = rs.count(True)
    roles = list(rs.skip(pre * (page - 1)).limit(pre))
    roles = sorted(roles, key=lambda x: x["permissions"])
    pers = permissions()
    for role in roles:
        role["permission_names"] = []
        for per in pers["permissions"]:
            if int(role["permissions"]) & int(per[1]):
                role["permission_names"].append(per[0])
    data["roles"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=objid_to_str(roles))
    return data


def add_role():

    name = request.argget.all('name').strip()
    instructions = request.argget.all('instructions').strip()
    default = int(request.argget.all('default', False).strip())
    temp_permissions = json_to_pyseq(request.argget.all('permissions', []))
    data = {
        'msg': gettext("Add a success"),
        'msg_type': "s",
        "custom_status": 201}

    permissions = 0x0
    for i in temp_permissions:
        permissions = permissions | int(i)

    s, r = arg_verify(reqargs=[(gettext("name"), name)], required=True)
    if not s:
        return r
    elif not mdbs["user"].db.role.find_one({gettext("name"): name}):

        # 权限检查
        user_role = mdbs["user"].db.role.find_one(
            {"_id": ObjectId(current_user.role_id)})
        if get_num_digits(user_role["permissions"]
                          ) <= get_num_digits(permissions):
            data = {
                "msg": gettext(
                    "The current user permissions are lower than the permissions that you want to add,"
                    " without permission to add"),
                "msg_type": "w",
                "custom_status": 401}
            return data

        if default:
            if not mdbs["user"].db.role.find_one({"default": {"$in": [1, True]}}):
                mdbs["user"].db.role.insert_one({"name": name,
                                             "instructions": instructions,
                                             'permissions': permissions,
                                             "default": default})
            else:
                data = {
                    'msg': gettext("Existing default role"),
                    'msg_type': "w",
                    "custom_status": 403}
        else:
            mdbs["user"].db.role.insert_one({"name": name,
                                         "instructions": instructions,
                                         'permissions': permissions,
                                         "default": default})

    else:
        data = {
            'msg': gettext("Role name already exists"),
            'msg_type': "w",
            "custom_status": 403}

    return data


def edit_role():

    rid = request.argget.all('id').strip()
    name = request.argget.all('name').strip()
    instructions = request.argget.all('instructions').strip()
    default = int(request.argget.all('default', 0))
    temp_permissions = json_to_pyseq(request.argget.all('permissions', []))

    permissions = 0x0
    for i in temp_permissions:
        permissions = permissions | int(i)

    s, r = arg_verify(reqargs=[(gettext("name"), name)], required=True)
    if not s:
        return r

    data = {
        "msg": gettext(
            "The current user permissions are lower than the permissions you want to modify,"
            " without permission to modify"),
        "msg_type": "w",
        "custom_status": 401}
    user_role = mdbs["user"].db.role.find_one(
        {"_id": ObjectId(current_user.role_id)})
    # 如果当前用户的权限最高位 小于 要修改成的这个角色权重的最高位,是不可以的
    if get_num_digits(user_role["permissions"]) < get_num_digits(permissions):
        return data
    elif get_num_digits(user_role["permissions"]) == get_num_digits(permissions):
        role = {
            "name": name,
            "instructions": instructions,
        }
        r = mdbs["user"].db.role.update_one(
            {"_id": ObjectId(rid)}, {"$set": role})
        if not r.modified_count:
            data = {
                'msg': gettext("No changes"),
                'msg_type': "w",
                "custom_status": 201}
        else:
            data = {
                "msg": gettext("The highest permission of the current user is equal to that of the selected permission."
                               " You can only modify the name and profile."),
                "msg_type": "s",
                "custom_status": 201
            }
        return data

    old_role = mdbs["user"].db.role.find_one({"_id": ObjectId(rid)})
    # 如果当前用户的权限最高位 小于 要修改角色的权限,也是不可以
    if old_role and get_num_digits(old_role["permissions"]) >= get_num_digits(user_role["permissions"]):
        return data

    elif old_role and get_num_digits(old_role["permissions"]) == get_num_digits(user_role["permissions"]):
        role = {
            "name": name,
            "instructions": instructions,
        }
        r = mdbs["user"].db.role.update_one(
            {"_id": ObjectId(rid)}, {"$set": role})
        if not r.modified_count:
            data = {
                'msg': gettext("No changes"),
                'msg_type': "w",
                "custom_status": 201}
        else:
            data = {
                "msg": gettext("The highest permission of the current user is equal to that of the role to be modified."
                               "Only the name and introduction can be modified."),
                "msg_type": "s",
                "custom_status": 201
            }
        return data

    else:
        role = {
            "name": name,
            "instructions": instructions,
            'permissions': permissions,
            "default": default
        }

    data = {
        'msg': gettext("Save success"),
        'msg_type': "s",
        "custom_status": 201}
    if not mdbs["user"].db.role.find_one({"name": name, "_id": {"$ne": ObjectId(rid)}}):
        if default:
            if not mdbs["user"].db.role.find_one(
                    {"default": {"$in": [1, True]}, "_id": {"$ne": ObjectId(rid)}}):
                r = mdbs["user"].db.role.update_one(
                    {"_id": ObjectId(rid)}, {"$set": role})
                if not r.modified_count:
                    data = {
                        'msg': gettext("No changes"),
                        'msg_type': "w",
                        "custom_status": 201}
            else:
                data = {
                    'msg': gettext("Existing default role"),
                    'msg_type': "w",
                    "custom_status": 403}
        else:
            r = mdbs["user"].db.role.update_one(
                {"_id": ObjectId(rid)}, {"$set": role})
            if not r.modified_count:
                data = {
                    'msg': gettext("No changes"),
                    'msg_type': "w",
                    "custom_status": 201}

    else:
        data = {
            'msg': gettext("Role name already exists"),
            'msg_type': "w",
            "custom_status": 403}

    return data


def delete_role():

    ids = json_to_pyseq(request.argget.all('ids'))

    user_role = mdbs["user"].db.role.find_one(
        {"_id": ObjectId(current_user.role_id)})
    noper = 0
    exist_user_role = 0
    for rid in ids:
        rid = ObjectId(rid)
        # 权限检查
        old_role = mdbs["user"].db.role.find_one({"_id": rid})
        # 如果当前用户的权限最高位 小于 要删除角色的权限,也是不可以
        if old_role and get_num_digits(
                old_role["permissions"]) >= get_num_digits(
                user_role["permissions"]):
            noper += 1
            continue

        if mdbs["user"].db.user.find(
                {"role_id": rid, "is_delete": {"$in": [0, False, None]}}).count(True):
            exist_user_role += 1
        else:
            mdbs["user"].db.role.delete_many({"_id": rid})
    if not noper:
        data = {'msg': gettext('Delete the success, {} of the roles have users and cannot be deleted').format(
            exist_user_role), 'msg_type': 's', "custom_status": 204}
    else:
        data = {
            'msg': gettext(
                '{} role do not have permission to delete,'
                ' {} of the roles have users and cannot be deleted').format(
                noper,
                exist_user_role),
            'msg_type': 'w',
            "custom_status": 400}

    return data
