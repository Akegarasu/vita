#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from random import randint
from flask import request
from flask_babel import gettext
from flask_login import current_user, login_user
import time
from apps.core.auth.jwt_auth import JwtAuth
from apps.core.flask.reqparse import arg_verify
from apps.core.plug_in.manager import plugin_manager
from apps.core.template.get_template import get_email_html
from apps.modules.user.models.user import user_model
from apps.modules.user.process.get_or_update_user import get_one_user, insert_one_user
from apps.modules.user.process.user import User
from apps.utils.format.time_format import time_to_utcdate
from apps.utils.geo.ip_to_geo import reader_city
from apps.modules.user.process.sign_in_anomaly import AbnormalLogin
from apps.utils.send_msg.send_email import send_email
from apps.utils.validation.str_format import email_format_ver, mobile_phone_format_ver
from apps.utils.verify.img_verify_code import verify_image_code
from apps.app import mdbs
from apps.core.utils.get_config import get_config


def p_sign_in(
        username,
        password,
        code_url_obj,
        code,
        remember_me,
        use_jwt_auth=0):
    """
    用户登录函数
    :param adm:
    :return:
    """
    data = {}
    if current_user.is_authenticated and username in [current_user.username,
                                                      current_user.email,
                                                      current_user.mphone_num]:
        data['msg'] = gettext("Is logged in")
        data["msg_type"] = "s"
        data["custom_status"] = 201
        data['to_url'] = request.argget.all(
            'next') or get_config("login_manager", "LOGIN_IN_TO")
        return data

    # name & pass
    s, r = email_format_ver(username)
    s2, r2 = mobile_phone_format_ver(username)
    if s:
        user = get_one_user(email=username)
    elif s2:
        user = get_one_user(mphone_num=username)
    else:
        user = get_one_user(username=username)
    if not user:
        data = {
            "msg": gettext("Account or password error"),
            "msg_type": "e",
            "custom_status": 401}
        return data

    user = User(user["_id"])

    # 判断是否多次密码错误,是就要验证图片验证码
    user_p = mdbs["user"].db.user_login_log.find_one({'user_id': user.str_id})
    PW_WRONG_NUM_IMG_CODE = get_config(
        "login_manager", "PW_WRONG_NUM_IMG_CODE")
    if user_p and 'pass_error' in user_p and user_p['pass_error'] >= PW_WRONG_NUM_IMG_CODE:
        # 图片验证码验证
        r = verify_image_code(code_url_obj, code)
        if not r:

            data["open_img_verif_code"] = True
            data['msg'] = gettext("Verification code error")
            data["msg_type"] = "e"
            data["custom_status"] = 401
            return data

    # 密码验证
    if user and user.verify_password(password) and not user.is_delete:
        if user.is_active:
            if use_jwt_auth:
                # 使用的时jwt验证
                # 获取token
                jwt_auth = JwtAuth()
                data["auth_token"] = jwt_auth.get_login_token(user)
                client = "app"
            else:
                login_user(user, remember_me)
                client = "browser"
            # 记录登录日志
            login_log(user, client)

            data['msg'] = gettext("Sign in success")
            data["msg_type"] = "s"
            data["custom_status"] = 201
            data["to_url"] = request.argget.all(
                'next') or get_config("login_manager", "LOGIN_IN_TO")
            return data

        # 未激活
        data['msg'] = gettext("Account is inactive or frozen")
        data["msg_type"] = "w"
        data["custom_status"] = 401

    else:
        # 密码错误
        mdbs["user"].db.user_login_log.update_one({'user_id': user.str_id},
                                              {"$inc": {"pass_error": 1}},
                                              upsert=True)

        # 判断是否多次密码错误
        if user_p and 'pass_error' in user_p and user_p['pass_error'] >= PW_WRONG_NUM_IMG_CODE:
            # 图片验证码验证码
            data["open_img_verif_code"] = True

        data['msg'] = gettext("Account or password error")
        data["msg_type"] = "e"
        data["custom_status"] = 401
    return data


def login_log(user, client):
    """
    登录日志操作
    :param user: 用户对象实例
    :return:
    """

    # 更新登录日志
    login_info = {
        'time': time.time(),
        'ip': request.remote_addr,
        'geo': reader_city(request.remote_addr),
        'client': client
    }

    user_login_log = mdbs["user"].db.user_login_log.find_one(
        {'user_id': user.str_id})
    if user_login_log and "login_info" in user_login_log:
        login_infos = user_login_log["login_info"]
    else:
        login_infos = []

    login_infos.append(login_info)
    than_num = len(login_infos) - \
        get_config("weblogger", "SING_IN_LOG_KEEP_NUM")
    if than_num > 0:
        del login_infos[0:than_num]
    mdbs["user"].db.user_login_log.update_one({'user_id': user.str_id},
                                          {"$set": {"pass_error": 0,
                                                    "login_info": login_infos}
                                           },
                                          upsert=True)

    # 检查登录地区是否异常
    anl = AbnormalLogin(login_infos[0:-1], login_info["geo"])
    abr = anl.area()
    if abr == "abnormal":
        # 发送邮件
        subject = gettext("Abnormal login")
        try:
            location = "{}/{}/{}".format(
                login_info["geo"]["subdivisions"]["name"],
                login_info["geo"]["country"]["name"],
                login_info["geo"]["continent"]["name"]
            )
        except BaseException:
            location = None
        if location:
            body = [
                gettext("Abnormal login"),
                gettext("Your account {} , is logined in {} on {} [UTC Time].").format(
                    user.email,
                    location,
                    time_to_utcdate(tformat="%Y-%m-%d %H:%M:%S")
                )
            ]
            data = {
                "title": subject,
                "username": user["username"],
                "body": body,
                "site_url": get_config("site_config", "SITE_URL")
            }
            html = get_email_html(data)

            msg = {
                "subject": subject,
                "recipients": [user["email"]],
                "html_msg": html
            }
            send_email(msg=msg, ctype="nt")


def third_party_sign_in(platform_name):
    """
    第三方登录回调函数
    :param hook_name: 第三方登录钩子名称,如:"wechat_login"
    :return:
    """

    # 检测插件
    data = plugin_manager.call_plug(hook_name="{}_login".format(platform_name),
                                    request_argget_all=request.argget.all)
    if data == "__no_plugin__":
        data = {
            "msg": gettext("No login processing plugin for this platform, please install the relevant plugin first"),
            "msg_type": "e",
            "custom_status": 400}
        return data

    unionid = data.get("unionid")
    # 检测用户是否等录过
    query = {
        "login_platform.{}.unionid".format(platform_name): unionid
    }
    user = mdbs["user"].db.user.find_one(query)
    if user:
        # 此用户已经在当前平台登录过, 直接登录
        user = User(user["_id"])
        if user.is_active:
            login_user(user, False)

            # 记录登录日志
            login_log(user, client="unknown:{}".format(platform_name))
            data = {
                "msg": gettext("Sign in success"),
                "msg_type": "s",
                "custom_status": 201}
        else:

            # 未激活
            data = {
                "msg": gettext("Account is inactive or frozen"),
                "msg_type": "w",
                "custom_status": 401}

    else:
        # 第一次登录, 注册信息
        # 用户基本信息
        nickname = "{}_{}".format(
            data.get("nickname"), randint(
                10000000, 99999999))
        gender = data.get("gender")
        email = data.get("email")
        avatar_url = data.get("avatar_url")
        province = data.get("province")
        city = data.get("city")
        country = data.get("country")

        address = {"province": province, "city": city, "country": country}
        s, r = arg_verify(reqargs=[("unionid", unionid)], required=True)
        if not s:
            return r
        s, r = arg_verify(
            reqargs=[
                (gettext("gender"), gender)], only=[
                "secret", "m", "f"])
        if not s:
            return r

        role_id = mdbs["user"].db.role.find_one(
            {"default": {"$in": [True, 1]}})["_id"]
        user = user_model(
            unionid=unionid,
            platform_name=platform_name,
            username=nickname,
            email=email,
            mphone_num=None,
            password=None,
            custom_domain=-1,
            address=address,
            avatar_url=avatar_url,
            role_id=role_id,
            active=True
        )
        r = insert_one_user(updata=user)

        if r.inserted_id:

            data = {'msg': gettext('Registered successfully'),
                    'to_url': '/sign-in',
                    'msg_type': 's', "custom_status": 201}
        else:
            data = {'msg': gettext('Data saved incorrectly, please try again'),
                    'msg_type': 'e', "custom_status": 400}
    return data
