#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import math
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.configs.sys_config import SUPER_PER, PRESERVE_PERS, GET_ALL_PERS_CACHE_KEY, \
    GET_DEFAULT_SYS_PER_CACHE_KEY
from apps.core.flask.permission import get_permission
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.number import get_num_digits
from apps.utils.format.obj_format import objid_to_str, json_to_pyseq, str_to_num
from apps.utils.paging.paging import datas_paging
from apps.app import cache, mdbs


def permission():
    """
    获取一个权限
    :return:
    """
    tid = request.argget.all('id').strip()
    data = {}
    data["per"] = mdbs["user"].db.permission.find_one({"_id": ObjectId(tid)})
    if not data["per"]:
        data = {
            'msg': gettext("The specified permission is not found"),
            'msg_type': "w",
            "custom_status": 404}
    else:
        data["per"]["_id"] = str(data["per"]["_id"])
        data["per"]["pos"] = get_num_digits(data["per"]["value"])

    return data


def permissions_details():
    """
    获取多个权限的详情
    :return:
    """

    data = {}
    page = str_to_num(request.argget.all('page', 1))
    pre = str_to_num(request.argget.all('pre', 10))
    rs = mdbs["user"].db.permission.find({})
    data_cnt = rs.count(True)
    roles = list(rs.skip(pre * (page - 1)).limit(pre))
    roles = sorted(roles, key=lambda x: x["value"])
    for role in roles:
        role["pos"] = get_num_digits(role["value"])
    data["pers"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=objid_to_str(roles))

    return data


def permissions():
    """
    只获取name,value, explain,以及已使用的权重位置
    :return:
    """

    data = []
    positions = list(range(1, get_num_digits(SUPER_PER) + 1))
    for per in mdbs["user"].dbs["permission"].find(
            {"value": {"$exists": True}}).sort([("value", -1)]):
        temp_pos = get_num_digits(per["value"])
        if temp_pos in positions:
            positions.remove(temp_pos)
        data.append((per["name"], per["value"], per["explain"]))
    data = {
        "permissions": sorted(
            data,
            key=lambda x: x[1]),
        "positions": positions}
    return data


def add_per():

    name = request.argget.all('name', '').strip()
    explain = request.argget.all('explain')
    default = int(request.argget.all('is_default', 0).strip())
    position = str_to_num(request.argget.all('position', 0))
    data = {
        'msg': gettext("Add a success"),
        'msg_type': "s",
        "custom_status": 201}

    s, r = arg_verify(
        reqargs=[
            (gettext("name"), name), (gettext("position"), position)], required=True)
    if not s:
        return r

    hightest_pos = get_num_digits(SUPER_PER)
    permissions = int(math.pow(2, position - 1))
    if hightest_pos > hightest_pos and position < 1:
        data = {
            'msg': gettext(
                "Must be an integer greater than 0,"
                " less than or equal to {}".format(hightest_pos)),
            'msg_type': "w",
            "custom_status": 403}

    elif mdbs["user"].db.permission.find_one({"name": name}):
        data = {'msg': gettext("Permission name or valready exists"),
                'msg_type': "w", "custom_status": 403}

    elif mdbs["user"].db.permission.find_one({"value": permissions}):
        data = {'msg': gettext('Location has been used'),
                'msg_type': "w", "custom_status": 403}
    else:
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

        mdbs["user"].db.permission.insert_one({"name": name,
                                           "explain": explain,
                                           'value': permissions,
                                           "is_default": default})
        cache.delete(key=GET_DEFAULT_SYS_PER_CACHE_KEY, db_type="redis")
        cache.delete(key=GET_ALL_PERS_CACHE_KEY, db_type="redis")
    return data


def edit_per():

    tid = request.argget.all('id').strip()
    name = request.argget.all('name', '').strip()
    explain = request.argget.all('explain', '')
    default = int(request.argget.all('is_default', 0).strip())
    position = str_to_num(request.argget.all('position', 0))

    s, r = arg_verify(
        reqargs=[
            (gettext("name"), name), (gettext("position"), position)], required=True)
    if not s:
        return r

    hightest_pos = get_num_digits(SUPER_PER)
    if position > hightest_pos and position < 1:
        data = {
            'msg': gettext(
                "Must be an integer greater than 0,"
                " less than or equal to {}".format(hightest_pos)),
            'msg_type': "w",
            "custom_status": 403}
        return data

    data = {
        "msg": gettext(
            "The current user permissions are lower than the permissions you want to modify,"
            " without permission to modify"),
        "msg_type": "w",
        "custom_status": 401}
    user_role = mdbs["user"].db.role.find_one({"_id": ObjectId(current_user.role_id)})
    # 如果当前用户的权限最高位 小于 要修改成的这个角色权重的最高位,是不可以的
    permissions = int(math.pow(2, position - 1))
    if get_num_digits(user_role["permissions"]) < get_num_digits(permissions):
        return data
    elif get_num_digits(user_role["permissions"]) == get_num_digits(permissions):
        per = {
            "name": name,
            "explain": explain
        }
        r = mdbs["user"].db.permission.update_one({"_id": ObjectId(tid)}, {"$set": per})
        if not r.modified_count:
            data = {
                'msg': gettext("The highest permission of the current user is"
                               " equal to the highest permission to be modified,"
                               " and only the name and introduction can be modified"),
                'msg_type': "s",
                "custom_status": 201}
        else:
            data = {
                'msg': gettext("No changes"),
                'msg_type': "w",
                "custom_status": 201}
        return data
    else:
        per = {
            "name": name,
            "explain": explain,
            'value': permissions,
            "is_default": default
        }
    if mdbs["user"].db.permission.find_one(
            {"name": name, "_id": {"$ne": ObjectId(tid)}}):
        data = {
            'msg': gettext("Permission name already exists"),
            'msg_type': "w",
            "custom_status": 403}

    elif mdbs["user"].db.permission.find_one({"value": permissions, "_id": {"$ne": ObjectId(tid)}}):
        data = {
            'msg': gettext('Location has been used'),
            'msg_type': "w",
            "custom_status": 403
        }
    else:
        old_per = mdbs["user"].db.permission.find_one(
            {
                "_id": ObjectId(tid),
                "value": {"$exists": True}
            }
        )
        if old_per:
            old_per_value = old_per["value"]
            r = mdbs["user"].db.permission.update_one({"_id": ObjectId(tid)}, {"$set": per})
            if not r.modified_count:
                data = {
                    'msg': gettext("No changes"),
                    'msg_type': "w",
                    "custom_status": 201}
            else:
                r = update_role_and_api_per(old_per_value, new_per_value=0)
                updated_rolename = r["updated_rolename"]
                msg_updated_rolename = gettext("The role of the chain reaction is: \n")
                if updated_rolename:
                    for ur in updated_rolename:
                        msg_updated_rolename = '{}, "{}"'.format(msg_updated_rolename, ur)
                else:
                    msg_updated_rolename = '{} 0'.format(msg_updated_rolename)
                # 刷新缓存
                cache.delete(key=GET_DEFAULT_SYS_PER_CACHE_KEY, db_type="redis")
                cache.delete(key=GET_ALL_PERS_CACHE_KEY, db_type="redis")
                data = {
                    'msg': gettext("The update is successful. {}".format(msg_updated_rolename)),
                    'msg_type': "s",
                    "custom_status": 201}
        else:
            data = {
                'msg': gettext("Update failed"),
                'msg_type': "w",
                "custom_status": 400}
    return data


def delete_per():

    ids = json_to_pyseq(request.argget.all('ids'))
    user_role = mdbs["user"].db.role.find_one(
        {"_id": ObjectId(current_user.role_id)})

    unauth_del_pers = []  # 无权删除的
    preserve = []  # 必须保留的
    need_remove = []
    need_remove_per_value = []

    for tid in ids:
        tid = ObjectId(tid)
        # 权限检查
        old_per = mdbs["user"].db.permission.find_one({"_id": tid})
        # 如果当前用户的权限最高位 小于 要删除角色的权限,也是不可以
        if old_per and get_num_digits(
                old_per["value"]) >= get_num_digits(
                user_role["permissions"]):
            unauth_del_pers.append(old_per["name"])
            continue
        if old_per["name"] in PRESERVE_PERS or ("is_default" in old_per and old_per["is_default"]):
            preserve.append(old_per["name"])
            continue
        need_remove.append(tid)
        need_remove_per_value.append(old_per["value"])

    # Delete
    msg_updated_rolename = ""
    if need_remove:

        mdbs["user"].db.permission.delete_many(
            {"_id": {"$in": need_remove}, "name": {"$nin": PRESERVE_PERS}})
        # 删除后必须更新使用了该权限的role和api&page
        updated_rolename = []
        for v in need_remove_per_value:
            r = update_role_and_api_per(old_per_value=v, new_per_value=0)
            updated_rolename.extend(r["updated_rolename"])

        msg_updated_rolename = gettext("The role of the chain reaction is: \n")
        if updated_rolename:
            updated_rolename = list(set(updated_rolename))
            for ur in updated_rolename:
                msg_updated_rolename = '{}, "{}"'.format(
                    msg_updated_rolename, ur)

        cache.delete(key=GET_DEFAULT_SYS_PER_CACHE_KEY, db_type="redis")
        cache.delete(key=GET_ALL_PERS_CACHE_KEY, db_type="redis")

    if not unauth_del_pers and not preserve:
        data = {
            'msg': gettext(
                'Successfully deleted. {}'.format(msg_updated_rolename)),
            'msg_type': 'success',
            "custom_status": 204}
    else:
        warning_msg = ""
        if unauth_del_pers:
            warning_msg = gettext('No permission to delete {}. ').format(
                ",".join(unauth_del_pers))
        elif preserve:
            warning_msg = gettext("{}{} are permissions that must be retained.").format(
                warning_msg, ",".join(preserve))
        data = {'msg': warning_msg, 'msg_type': 'warning', "custom_status": 400}

    return data


def update_role_and_api_per(old_per_value, new_per_value=0):
    """
    更新所有使用了old_per的role和api
    :param old_per:
    :param new_per:
    :return:
    """
    # 更新使用了该权限的role
    # 当前所有的用户角色
    updated_rolename = []
    roles = mdbs["user"].db.role.find({})
    for role in roles:
        if int(role["permissions"]) & int(old_per_value) and not (
                int(role["permissions"]) & int(get_permission("ROOT"))):
            role_new_per = (role["permissions"] - old_per_value) | new_per_value
            mdbs["user"].db.role.update_many({"_id": role["_id"]}, {
                                      "$set": {"permissions": role_new_per}})
            updated_rolename.append(role["name"])

    # 更新使用了该权限的url or page
    # 当前所有自定义权限url
    urls = list(mdbs["sys"].db.sys_urls.find(
        {"custom_permission": {"$ne": {}, "$exists": True}}))
    for url in urls:
        for method, v in url["custom_permission"].items():
            if v & old_per_value:
                # 修改
                url["custom_permission"][method] = (v - old_per_value) | new_per_value

        # 更新
        mdbs["sys"].db.sys_urls.update_one(
            {"_id": url["_id"]}, {"$set": {"custom_permission": url["custom_permission"]}})

        cache.delete_autokey(
            fun="get_sys_url",
            db_type="redis",
            url=url['url'].rstrip("/"))

    return {"updated_rolename": updated_rolename}
