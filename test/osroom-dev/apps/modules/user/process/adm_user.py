#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from bson.objectid import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user
from werkzeug.security import generate_password_hash

from apps.core.flask.reqparse import arg_verify
from apps.core.template.get_template import get_email_html
from apps.core.utils.get_config import get_config
from apps.modules.user.models.user import user_model
from apps.modules.user.process.get_or_update_user import get_one_user, update_one_user, clean_get_one_user_cache, \
    insert_one_user
from apps.utils.format.number import get_num_digits
from apps.utils.format.obj_format import json_to_pyseq, str_to_num
from apps.utils.paging.paging import datas_paging
from apps.app import mdbs, cache
from apps.utils.send_msg.send_email import send_email
from apps.utils.send_msg.send_message import send_mobile_msg
from apps.utils.upload.get_filepath import get_avatar_url
from apps.utils.validation.str_format import short_str_verifi, password_format_ver, mobile_phone_format_ver, \
    email_format_ver
from apps.utils.verify.msg_verify_code import verify_code


def add_user():

    email = request.argget.all('email')
    mobile_phone_number = str_to_num(request.argget.all('mobile_phone_number', 0))
    username = request.argget.all('username', '').strip()
    password = request.argget.all('password', '').strip()
    password2 = request.argget.all('password2', '').strip()

    data = {}
    # 用户名格式验证
    s1, r1 = short_str_verifi(username, project="username")
    # 密码格式验证
    s2, r2 = password_format_ver(password)
    if not s1:
        data = {'msg': r1, 'msg_type': "e", "custom_status": 422}
    elif mdbs["user"].db.user.find_one({"username": username}):
        # 是否存在用户名
        data = {
            'msg': gettext("Name has been used"),
            'msg_type': "w",
            "custom_status": 403}
    elif not s2:
        data = {'msg': r2, 'msg_type': "e", "custom_status": 400}
        return data
    elif password2 != password:
        # 检验两次密码
        data = {
            'msg': gettext("The two passwords don't match"),
            'msg_type': "e",
            "custom_status": 400}
    if data:
        return data

    if email:
        # 邮件注册
        # 邮箱格式验证
        s, r = email_format_ver(email)
        if not s:
            data = {'msg': r, 'msg_type': "e", "custom_status": 422}
        elif mdbs["user"].db.user.find_one({"email": email}):
            # 邮箱是否注册过
            data = {
                'msg': gettext("This email has been registered in the site oh, please login directly."),
                'msg_type': "w",
                "custom_status": 403}
        if data:
            return data

    elif mobile_phone_number:
        # 手机注册
        s, r = mobile_phone_format_ver(mobile_phone_number)
        if not s:
            data = {'msg': r, 'msg_type': "e", "custom_status": 422}
        elif mdbs["user"].db.user.find_one({"mphone_num": mobile_phone_number}):
            # 手机是否注册过
            data = {
                'msg': gettext("This number has been registered in the site oh, please login directly."),
                'msg_type': "w",
                "custom_status": 403}

        if data:
            return data

    if not data:
        # 用户基本信息
        role_id = mdbs["user"].db.role.find_one(
            {"default": {"$in": [True, 1]}})["_id"]
        if not email:
            email = None
        if not mobile_phone_number:
            mobile_phone_number = None
        user = user_model(username=username,
                          email=email,
                          mphone_num=mobile_phone_number,
                          password=password,
                          custom_domain=-1,
                          role_id=str(role_id),
                          active=True,
                          is_adm_add_user=True)
        r = insert_one_user(updata=user)
        if r.inserted_id:
            if email:
                # 发送邮件
                subject = gettext("Registration success notification")
                body = [
                    gettext("Welcome to register {}.").format( get_config("site_config", "APP_NAME")),
                    gettext("{} registered the account successfully.").format(email)
                ]
                data = {
                    "title": subject,
                    "body": body,
                    "username": username,
                    "site_url": get_config("site_config", "SITE_URL")
                }
                html = get_email_html(data)

                msg = {
                    "subject": subject,
                    "recipients": [email],
                    "html_msg": html
                }
                send_email(msg=msg, ctype="nt")

            elif mobile_phone_number:
                # 发送短信
                content = gettext("[{}] Successful registration account.").format(
                    get_config("site_config", "APP_NAME")
                )
                send_mobile_msg(mobile_phone_number, content)

            data = {'msg': gettext('Added successfully'),
                    'msg_type': 's', "custom_status": 201}
    return data


def user():
    tid = request.argget.all('id').strip()
    data = {}
    data["user"] = get_one_user(user_id=str(tid))
    if not data["user"]:
        data = {
            'msg': gettext("The specified user is not found"),
            'msg_type': "w",
            "custom_status": 404}
    else:
        data["user"]["_id"] = str(data["user"]["_id"])
        data["user"]["role_id"] = str(data["user"]["role_id"])
    return data


def users():
    """
    Admin获取用户数据
    :return:
    """
    data = {}
    status = request.argget.all('status')
    page = int(request.argget.all('page', 1))
    pre = int(request.argget.all('pre', 10))
    keyword = request.argget.all('keyword', '').strip()
    if status == "normal" or not status:
        status = "normal"
        query_conditions = {
            "is_delete": {
                "$in": [
                    False, 0]}, "active": {
                "$in": [
                    True, 1]}}
    elif status == "inactive":
        query_conditions = {
            "is_delete": {
                "$in": [
                    False, 0]}, "active": {
                "$in": [
                    False, 0]}}
    elif status == "cancelled":
        query_conditions = {"is_delete": {"$in": [True, 1]}}

    if keyword:
        keyword = {"$regex": keyword, "$options": "$i"}
        query_conditions["$or"] = [{"username": keyword},
                                   {"email": keyword},
                                   {"custom_domain": keyword}
                                   ]
    us = mdbs["user"].db.user.find(query_conditions, {"password": 0})
    data_cnt = us.count(True)
    users = list(us.sort([("create_at", -1)]
                         ).skip(pre * (page - 1)).limit(pre))
    roles = list(mdbs["user"].db.role.find({}))
    for user in users:
        user['_id'] = str(user['_id'])
        for role in roles:
            if ObjectId(user["role_id"]) == role["_id"]:
                user["role_name"] = role["name"]

        user_login_log = mdbs["user"].db.user_login_log.find_one(
            {"user_id": user["_id"]}, {"user_id": 0})
        user["user_login_log"] = []
        if user_login_log:
            user_login_log["_id"] = str(user_login_log["_id"])
            # if user_login_log["login_info"]:
            #     user_login_log["login_info"] = sorted(user_login_log["login_info"],
            #                                           key=lambda x:x["time"],
            #                                           reverse=True)
            user["user_login_log"] = user_login_log

        user_op_log = mdbs["user"].db.user_op_log.find_one(
            {'user_id': user["_id"]}, {"user_id": 0})
        user["user_op_log"] = []
        if user_op_log:
            user_op_log["_id"] = str(user_op_log["_id"])
            user_op_log["logs"] = sorted(user_op_log["logs"],
                                         key=lambda x: x["time"],
                                         reverse=True)
            user["user_op_log"] = user_op_log

        user["role_id"] = str(user["role_id"])
        user["avatar_url"]["url"] = get_avatar_url(user["avatar_url"])

    data["users"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=users)
    data["status"] = status
    return data


def user_edit():
    """
    用户编辑
    :return:
    """
    tid = request.argget.all('id')
    role_id = request.argget.all('role_id')
    email = request.argget.all('email')
    password = request.argget.all('password')
    active = str_to_num(request.argget.all('active', 0))

    s, r = arg_verify(
        reqargs=[
            ("id", tid), ("role_id", role_id)], required=True)
    if not s:
        return r

    data = {
        'msg': gettext("Update success"),
        'msg_type': "s",
        "custom_status": 201}

    if not email:
        email = None
    update_data = {
        'role_id': role_id,
        'active': active,
        "email": email
    }
    user = get_one_user(user_id=str(tid))
    if user:
        # 权限检查
        current_user_role = mdbs["user"].db.role.find_one(
            {"_id": ObjectId(current_user.role_id)})
        edit_user_role = mdbs["user"].db.role.find_one(
            {"_id": ObjectId(user["role_id"])})
        if edit_user_role \
                and get_num_digits(current_user_role["permissions"]) \
                <= get_num_digits(edit_user_role["permissions"]):
            # 没有权限修改
            data = {
                "msg_type": "w",
                "msg": gettext("No permission modification"),
                "custom_status": 401}
            return data

    if email:
        # 邮件注册
        # 邮箱格式验证
        s, r = email_format_ver(email)
        if not s:
            data = {'msg': r, 'msg_type': "e", "custom_status": 422}
            return data
        elif mdbs["user"].db.user.find_one({"email": email, "_id": {"$ne": ObjectId(tid)}}):
            # 邮箱是否注册过
            data = {
                'msg': gettext("This email has been registered in the site oh, please login directly."),
                'msg_type': "w",
                "custom_status": 403}
            return data
    if password:
        # 密码格式验证
        s, r = password_format_ver(password)
        if not s:
            data = {'msg': r, 'msg_type': "e", "custom_status": 422}
            return data
        
    if password:
        password = generate_password_hash(password)
        update_data["password"] = password
    r = update_one_user(user_id=str(tid), updata={"$set": update_data})
    if not r.modified_count:
        data = {
            'msg': gettext("No changes"),
            'msg_type': "w",
            "custom_status": 201}
    return data


def user_del():
    ids = json_to_pyseq(request.argget.all('ids', []))
    permanent = request.argget.all('permanent', 0)
    try:
        permanent = int(permanent)
    except BaseException:
        pass
    noper = 0
    temp_ids = ids[:]
    ids = []
    for tid in temp_ids:
        # 检查是否有权限
        current_user_role = mdbs["user"].db.role.find_one({"_id": ObjectId(current_user.role_id)})
        rm_user = get_one_user(user_id=str(tid))
        rm_user_role = mdbs["user"].db.role.find_one({"_id": ObjectId(rm_user["role_id"])})
        if get_num_digits(current_user_role["permissions"]) <= get_num_digits(rm_user_role["permissions"]):
            # 没有权限删除
            continue
        ids.append(ObjectId(tid))

    if not permanent:
        update_data = {
            'is_delete': 1
        }
        r = mdbs["user"].db.user.update_many(
            {"_id": {"$in": ids}}, {"$set": update_data})
        if r.modified_count:
            for uid in ids:
                clean_get_one_user_cache(user_id=uid)

            data = {
                'msg': gettext("Has recovered {} users, {} users can not operate").format(
                    r.modified_count,
                    noper),
                'msg_type': "s",
                "custom_status": 201}
        else:
            data = {
                'msg': gettext("Recycle user failed.May not have permission"),
                'msg_type': "w",
                "custom_status": 401}
    else:
        # 永久删除
        r = mdbs["user"].db.user.delete_many(
            {"_id": {"$in": ids}, "is_delete": {"$in": [1, True]}})
        if r.deleted_count:
            data = {
                'msg': gettext(
                    "{} users have been deleted and {} users can not be deleted".format(
                        r.deleted_count,
                        noper)),
                'msg_type': "s",
                "custom_status": 204}
        else:
            data = {
                'msg': gettext("Failed to delete.May not have permission"),
                'msg_type': "w",
                "custom_status": 401}

    return data


def user_restore():
    ids = json_to_pyseq(request.argget.all('ids', []))
    noper = 0
    re_ids = []
    for uid in ids:
        # 检查是否有权限
        current_user_role = mdbs["user"].db.role.find_one(
            {"_id": ObjectId(current_user.role_id)})
        re_user = get_one_user(user_id=str(uid))
        re_user_role = mdbs["user"].db.role.find_one(
            {"_id": ObjectId(re_user["role_id"])})
        if get_num_digits(
                current_user_role["permissions"]) <= get_num_digits(
                re_user_role["permissions"]):
            # 没有权限恢复
            noper += 1
            continue
        re_ids.append(ObjectId(uid))

    update_data = {
        'is_delete': 0
    }

    r = mdbs["user"].db.user.update_many(
        {"_id": {"$in": re_ids}}, {"$set": update_data})
    if r.modified_count:
        for uid in re_ids:
            clean_get_one_user_cache(user_id=uid)

        data = {
            'msg': gettext(
                "Restore the {} users,The other {} users have no power control".format(
                    r.modified_count,
                    noper)),
            'msg_type': "s",
            "custom_status": 201}
    else:
        data = {
            'msg': gettext("Restore the failure.May not have permission"),
            'msg_type': "w",
            "custom_status": 401}
    return data


def user_activation():
    active = int(request.argget.all('active', 0))
    ids = json_to_pyseq(request.argget.all('ids', []))
    noper = 0
    ac_ids = []
    for uid in ids:
        # 检查是否有权限
        current_user_role = mdbs["user"].db.role.find_one(
            {"_id": ObjectId(current_user.role_id)})
        re_user = get_one_user(user_id=str(uid))
        re_user_role = mdbs["user"].db.role.find_one(
            {"_id": ObjectId(re_user["role_id"])})
        if get_num_digits(
                current_user_role["permissions"]) <= get_num_digits(
                re_user_role["permissions"]):
            # 没有权限恢复
            noper += 1
            continue
        ac_ids.append(ObjectId(uid))

    update_data = {
        'active': active
    }

    r = mdbs["user"].db.user.update_many(
        {"_id": {"$in": ac_ids}}, {"$set": update_data})
    if r.modified_count:
        for uid in ac_ids:
            clean_get_one_user_cache(user_id=uid)

        data = {
            'msg': gettext(
                "{} user activation is successful, {} no permission to operate".format(
                    r.modified_count,
                    noper)),
            'msg_type': "s",
            "custom_status": 201}
    else:
        data = {
            'msg': gettext("Activation failed.May not have permission"),
            'msg_type': "w",
            "custom_status": 401}
    return data
