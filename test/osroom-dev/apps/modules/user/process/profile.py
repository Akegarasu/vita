#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user
import time

from apps.modules.user.process.get_or_update_user import update_one_user
from apps.modules.user.process.user_profile_process import get_user_all_info, get_user_public_info, \
    delete_user_info_cache
from apps.utils.validation.str_format import ver_user_domainhacks, short_str_verifi, content_attack_defense
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import json_to_pyseq, str_to_num
from apps.utils.format.time_format import time_to_utcdate
from apps.app import mdbs
from apps.utils.validation.str_format import url_format_ver


def public_profile():
    """
    获取用户公开信息
    :return:
    """
    data = {}
    user_id = request.argget.all('user_id')
    is_basic = str_to_num(request.argget.all('is_basic', 1))
    if not user_id or user_id == "None":
        data = {
            'd_msg': gettext('Lack of parameters "user_id"'),
            'd_msg_type': "e",
            "custom_status": 400}
        return data

    try:
        ObjectId(user_id)
    except BaseException:
        data = {
            'd_msg': gettext('This may be a visitor"'),
            'd_msg_type': "e",
            "custom_status": 400}
        return data

    s, r = get_user_public_info(user_id=user_id,
                                is_basic=is_basic,
                                current_user_isauth=current_user.is_authenticated)
    if not s:
        data = {'msg': r, 'msg_type': "w", "custom_status": 400}
    else:
        data["user"] = r
    return data


def all_profile():
    """
    获取用户信息
    :return:
    """
    is_basic = str_to_num(request.argget.all('is_basic', 1))
    data = {}
    s, r = get_user_all_info(user_id=current_user.str_id,
                             is_basic=is_basic,
                             current_user_isauth=current_user.is_authenticated)
    if not s:
        data = {'msg': r, 'msg_type': "w", "custom_status": 400}
    else:
        data["user"] = r
    return data


def profile_update():
    """
    用户信息更新
    :return:
    """
    gender = request.argget.all('gender', 'secret')
    birthday = request.argget.all('birthday')
    homepage = request.argget.all('homepage')
    address = json_to_pyseq(request.argget.all('address', {}))
    info = request.argget.all('info')
    if len(birthday) != 8:
        data = {
            'msg': gettext("The date of birth requires an 8-digit date,Such as '{}'").format(
                time_to_utcdate(
                    tformat="%Y%m%d")),
            'msg_type': "e",
            "custom_status": 400}
        return data
    birthday = int(birthday)
    s, r = arg_verify(
        reqargs=[
            (gettext("gender"), gender)], only=[
            "secret", "m", "f"])
    if not s:
        return r
    addr_keys = ['countries', 'provinces', 'city', 'district', 'detailed']
    for k, v in address.items():
        if not (k in addr_keys) or not isinstance(v, str):
            data = {
                'msg': gettext("Address format is not in conformity with the requirements"),
                'msg_type': "e",
                "custom_status": 400}
            return data
    if homepage:
        s, r = url_format_ver(homepage)
        if not s:
            return {"msg": r, "msg_type": "w", "custom_status": 403}

    r = content_attack_defense(info)
    if r["security"] < 100:
        data = {
            'msg': gettext("User profile information is illegal"),
            'msg_type': "e",
            "custom_status": 400}
        return data
    update_data = {
        'gender': gender,
        'homepage': homepage,
        'introduction': info,
        'birthday': birthday,
        'address': address
    }
    r = update_one_user(
        user_id=current_user.str_id, updata={
            "$set": update_data})

    if r.modified_count:
        # 清理user信息数据缓存
        delete_user_info_cache(user_id=current_user.str_id)
        data = {
            'msg': gettext("Update succeed"),
            'msg_type': "s",
            "custom_status": 201}
    else:
        data = {
            'msg': gettext("No changes"),
            'msg_type': "w",
            "custom_status": 201}
    return data


def user_basic_edit():
    """
    用户基础设置编辑
    :return:
    """
    username = request.argget.all('username')
    custom_domain = request.argget.all('custom_domain', '')
    editor = request.argget.all('editor')
    # username
    s, r = arg_verify(reqargs=[(gettext("username"), username)], required=True)
    if not s:
        return r
    r, s = short_str_verifi(username, "username")
    if not r:
        data = {'msg': s, 'msg_type': "e", "custom_status": 422}
        return data

    update_data = {}
    # custom_domain
    if mdbs["user"].db.user.find_one(
            {"_id": current_user.id, "custom_domain": -1}) and custom_domain.strip():
        r, s = ver_user_domainhacks(custom_domain)
        if r:
            update_data["custom_domain"] = custom_domain
        else:
            data = {'msg': s, 'msg_type': "e", "custom_status": 422}
            return data


    update_data["username"] = username
    # editor
    if editor and editor in ['rich_text', 'markdown']:
        update_data["editor"] = editor
    else:
        data = {
            'msg': gettext("The editor saves failure"),
            'msg_type': "e",
            "custom_status": 400}
        return data

    update_data["update_time"] = time.time()

    # 是否被使用
    if mdbs["user"].db.user.find_one(
            {"_id": {"$ne": current_user.id}, "username": username}):
        data = {
            'msg': gettext("Name has been used"),
            'msg_type': "w",
            "custom_status": 403}
    elif "custom_domain" in update_data.keys() \
            and mdbs["user"].db.user.find_one({"_id": {"$ne": current_user.id}, "custom_domain": custom_domain}):
        data = {
            'msg': gettext("Domain has been used"),
            'msg_type': "w",
            "custom_status": 403}
    elif "custom_domain" in update_data.keys() and mdbs["user"].db.user.find_one({"_id": current_user.id, "custom_domain": {"$ne": -1}}):
        data = {
            'msg': gettext("Personality custom domain cannot be modified"),
            'msg_type': "w",
            "custom_status": 400}
    else:
        r = update_one_user(
            user_id=current_user.str_id, updata={
                "$set": update_data})
        if not r.modified_count:
            data = {
                'msg': gettext("No changes"),
                'msg_type': "w",
                "custom_status": 201}
        else:
            delete_user_info_cache(user_id=current_user.str_id)
            data = {
                'msg': gettext("Update success"),
                'msg_type': "s",
                "custom_status": 201}

    return data
