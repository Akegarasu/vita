#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import datetime
from uuid import uuid1
import jwt
import time
from bson import ObjectId
from flask import current_app, request
from flask_babel import gettext
from apps.app import mdbs
from apps.core.utils.get_config import get_config
from apps.modules.user.process.get_or_update_user import update_one_user, get_one_user
from apps.modules.user.process.user import User


class JwtAuth:

    """
    JWT用户验证
    """

    @staticmethod
    def encode_auth_token(user_id, login_time):
        """
        生成认证Token
        :param user_id: <id>
        :param login_time: int(timestamp)
        :return: string
        """
        iat = datetime.datetime.utcnow()
        exp = iat + datetime.timedelta(days=0,
                                       seconds=get_config("rest_auth_token",
                                                          "LOGIN_LIFETIME"))

        try:
            payload = {
                'exp': exp,
                'iat': iat,
                'iss': 'osroom',
                'data': {
                    'id': user_id,
                    'login_time': login_time,
                    'cid': str(uuid1())
                }
            }
            return {
                "token": jwt.encode(
                    payload,
                    current_app.secret_key,
                    algorithm='HS256'),
                "cid": payload["data"]["cid"]}
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        验证Token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(
                auth_token,
                current_app.secret_key,
                leeway=get_config(
                    "rest_auth_token",
                    "LOGIN_LIFETIME"))
            if 'data' in payload and 'id' in payload['data']:
                return payload
            else:
                raise jwt.InvalidTokenError

        except jwt.ExpiredSignatureError:

            return gettext('The provided OSR-BearerToken has expired')

        except jwt.InvalidTokenError:
            return gettext('Invalid OSR-BearerToken')

    def get_login_token(self, user):
        """
        用户登录成功后调用此函数,记录登录并获取token
        :param user:
        :return: json
        """
        now_time = time.time()
        result = self.encode_auth_token(user.str_id, now_time)

        # 查看当前jwt验证的登录客户端数
        user_jwt = mdbs["user"].db.user.find_one(
            {"_id": user.id, "jwt_login_time": {"$exists": True}}, {"jwt_login_time": 1})
        if user_jwt:
            jwt_login_time = user_jwt["jwt_login_time"]
            keys = jwt_login_time.keys()
            if len(keys) >= get_config(
                "rest_auth_token",
                    "MAX_SAME_TIME_LOGIN"):
                earliest = 0
                earliest_cid = None
                for k, v in jwt_login_time.items():
                    if v < earliest or earliest == 0:
                        earliest = v
                        earliest_cid = k
                if earliest_cid:
                    del jwt_login_time[earliest_cid]
        else:
            jwt_login_time = {}

        jwt_login_time[result["cid"]] = now_time
        update_one_user(user_id=user.id,
                        updata={"$set": {"jwt_login_time": jwt_login_time}})
        return result["token"].decode()

    def user_identify(self):
        """
        用户鉴权
        :return: (status, )
        """

        auth_token = request.headers.get('OSR-BearerToken')
        if auth_token:

            payload = self.decode_auth_token(auth_token)
            if not isinstance(payload, str):
                user = User(ObjectId(payload['data']['id']))
                if not user:
                    result = (
                        None, gettext("User authentication failed, user does not exist"))
                else:
                    if user.jwt_login_time and \
                        payload['data']["cid"] in user.jwt_login_time and \
                            user.jwt_login_time[payload['data']["cid"]] == \
                            payload['data']['login_time']:
                        result = (True, user)
                    else:
                        result = (None, gettext(
                            'User authentication token expired or changed. '
                            'Please log in again for access')
                            )
            else:
                result = (None, gettext("Token is abnormal"))
        else:
            result = (
                None,
                gettext('No user authentication token provided "OSR-BearerToken"'))
        return result

    def clean_login(self):
        """
        清理用户登录
        :return:
        """

        auth_token = request.headers.get('OSR-BearerToken')
        if auth_token:
            payload = self.decode_auth_token(auth_token)
            if not isinstance(payload, str):
                user = get_one_user(user_id=str(payload['data']['id']))
                if not user:
                    result = (
                        None, gettext("User authentication failed, user does not exist"))
                else:
                    if payload['data']["cid"] in user["jwt_login_time"] and \
                            user["jwt_login_time"][payload['data']["cid"]] == \
                            payload['data']['login_time']:

                        # 清除退出当前客户端的登录时间信息
                        user = get_one_user(user_id=str(payload['data']['id']))

                        del user["jwt_login_time"][payload["data"]["cid"]]
                        update_one_user(
                            user_id=payload["data"]["id"], updata={
                                "$set": {
                                    "jwt_login_time": user["jwt_login_time"]}})

                        result = (True, "")
                    else:
                        result = (True, "")
            else:
                result = (None, payload)
        else:
            result = (
                None,
                gettext('No user authentication token provided "OSR-BearerToken"'))
        return result
