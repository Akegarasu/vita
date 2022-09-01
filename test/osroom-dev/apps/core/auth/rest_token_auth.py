#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import hashlib
import sys
import time
from gettext import gettext
from random import randint
from uuid import uuid1

from bson import ObjectId
from flask import current_app, request
from werkzeug.exceptions import Unauthorized

from apps.app import app, cache, csrf, mdbs, rest_session
from apps.configs.sys_config import REST_SECRET_TOKEN_CACHE_KEY, REST_SECRET_TOKEN_CACHE_TIMEOUT
from apps.core.utils.get_config import get_config
from apps.utils.format.obj_format import objid_to_str


class RestTokenAuth:

    """
    客户端验证
    """
    def is_exempt(self):
        view = app.view_functions.get(request.endpoint)
        if not view:
            return True
        if request.blueprint in csrf._exempt_blueprints:
            return True
        dest = '%s.%s' % (view.__module__, view.__name__)
        if dest in csrf._exempt_views:
            return True

        return False

    @staticmethod
    def encode_auth_token():
        """
        生成认证Token
        id:str
        :return: string
        """
        pyver_info = sys.version_info
        if pyver_info[0] == 3 and pyver_info[1] == 6:
            # 3.6版本以上才使用secrets
            import secrets
            tid = secrets.token_urlsafe()
        else:
            tid = "{}{}".format(str(uuid1()), randint(0, 999999))
            tid = hashlib.md5(tid.encode("UTF-8")).hexdigest()

        return {"token": tid}

    """
    SecretToken
    """

    def create_secret_token(self):
        """
        管理端创建secret token
        """

        tokens = mdbs["sys"].db.sys_token.find({"token_type": "secret_token"})
        if tokens.count(True) < 2:
            result = self.encode_auth_token()

            token = {"token_type": "secret_token",
                     "key": result["token"],
                     "token": result["token"],
                     "is_active": 1,
                     "time": time.time()}
            r = mdbs["sys"].db.sys_token.insert_one(token)
            token["_id"] = str(r.inserted_id)
            cache.delete(REST_SECRET_TOKEN_CACHE_KEY)
            return True, token
        return False, gettext("Create up to 2 tokens")

    def activate_secret_token(self, token_id):
        """
        激活secret token
        :return:
        """

        r = mdbs["sys"].db.sys_token.update_one(
            {
                "_id": ObjectId(token_id)
            },
            {
                "$set": {"is_active": 1}
            }
        )
        if r.modified_count:
            cache.delete(REST_SECRET_TOKEN_CACHE_KEY)
            return True, gettext("Activate token successfully")
        else:
            return False, gettext("Activation token failed")

    def disable_secret_token(self, token_id):
        """
        停用secret token
        :return:
        """
        token_count = mdbs["sys"].db.sys_token.find(
            {
                "token_type": "secret_token",
                "is_active": {
                    "$in": [1, True]
                }
            }).count(True)
        if token_count > 1:
            r = mdbs["sys"].db.sys_token.update_one(
                {
                    "_id": ObjectId(token_id)
                },
                {
                    "$set": {"is_active": 0}
                })

            if r.modified_count:
                cache.delete(REST_SECRET_TOKEN_CACHE_KEY)
                return True, gettext("Disable token successfully")
            else:
                return False, gettext("Disable token failed")
        else:
            return False, gettext("Keep at least one active token")

    def delete_secret_token(self, token_id):
        """
        删除token, 至少保留一个token
        :return:
        """

        if mdbs["sys"].db.sys_token.find(
                {
                    "token_type": "secret_token"
                }).count(True) > 1:
            r = mdbs["sys"].db.sys_token.delete_one({"_id": ObjectId(token_id)})
            if r.deleted_count > 0:
                cache.delete(REST_SECRET_TOKEN_CACHE_KEY)
                return True, gettext("Successfully deleted")
            else:
                return False, gettext("Delete failed")
        else:
            return False, gettext("Delete failed, keep at least one token")

    @property
    @cache.cached(
        key=REST_SECRET_TOKEN_CACHE_KEY,
        timeout=REST_SECRET_TOKEN_CACHE_TIMEOUT)
    def get_secret_tokens(self):
        token_info = mdbs["sys"].db.sys_token.find({"token_type": "secret_token"})
        if not token_info.count(True):
            s, r = self.create_secret_token()
            token_info = [r]
        else:
            token_info = objid_to_str(token_info)
        is_active_token = []
        for token in token_info:
            if token["is_active"]:
                is_active_token.append(token["token"])
        data = {"token_info": token_info, "is_active_token": is_active_token}
        return data

    def auth_rest_token(self):

        auth_token_type = None
        auth_header = request.headers.get('OSR-RestToken')
        if auth_header:
            # 使用RestToken验证
            is_malformed = False
            auth_header = auth_header.split(" ")
            if len(auth_header) >= 2:
                if auth_header[0] == "SecretToken":
                    auth_token_type = "secret_token"
                    # 使用的是SecretToken, 固定Token
                    if not auth_header[1] in self.get_secret_tokens["is_active_token"]:
                        # SecretToken无效
                        response = current_app.make_response(
                            gettext("Invalid SecretToken for OSR-RestsToken"))
                        raise SecretTokenError(
                            response.get_data(
                                as_text=True), response=response)

                elif auth_header[0] == "AccessToken":
                    auth_token_type = "access_token"
                    self.auth_access_token(auth_header[1])
                else:
                    # 格式不对
                    is_malformed = True
            else:
                is_malformed = True
            if is_malformed:
                response = current_app.make_response(
                    gettext(
                        "Token malformed, should be 'SecretToken <token>'"
                        " or 'AccessToken <token>' and 'ClientId <client_id>'"))
                raise SecretTokenError(
                    response.get_data(
                        as_text=True),
                    response=response)
        else:
            response = current_app.make_response(
                gettext(
                    'Token is miss, unconventional web browsing'
                    ' requests please provide "OSR-RestToken",'
                    ' otherwise provide "X-CSRFToken"'))
            raise OsrTokenError(
                response.get_data(
                    as_text=True),
                response=response)

        return auth_token_type

    """
    Client Token
    """

    def create_access_token(self):
        """
        创建client token, 用于rest api常用验证
        """
        r = self.auth_rest_token()
        if r == "secret_token":
            client_token = {
                "token": self.encode_auth_token()["token"],
                "expiration": time.time() +
                get_config(
                    "rest_auth_token",
                    "REST_ACCESS_TOKEN_LIFETIME")}
            sid = rest_session.set("access_token", client_token)
            if sid:
                data = {
                    "client_id": sid,
                    "access_token": client_token["token"]}
            else:
                data = {"msg": gettext("Failed to get, please try again"),
                        "msg_type": "w", "custom_status": 400}
        else:
            data = {
                "msg": gettext(
                    "The OSR-RestToken provided by the request header"
                    " is not a SecretToken"),
                "msg_type": "w",
                "custom_status": 400}
        return data

    def auth_access_token(self, token):
        """
        验证client id 与client token
        :return:
        """
        se_token = rest_session.get("access_token")
        if se_token:

            if se_token["token"] != token or se_token["expiration"] <= time.time():
                # 验证失败或者已过期
                response = current_app.make_response(
                    gettext("Invalid AccessToken or AccessToken has expired"))
                raise AccessTokenError(
                    response.get_data(
                        as_text=True),
                    response=response)
        else:

            # 找不到相关token
            response = current_app.make_response(
                gettext("Can not find the ClientId matching 'AccessToken'"))
            raise AccessTokenError(
                response.get_data(
                    as_text=True),
                response=response)


class SecretTokenError(Unauthorized):
    """
    错误请求类： SecretToken错误
    """
    description = gettext('SecretToken in OSr-RestToken is invalid')


class AccessTokenError(Unauthorized):
    """
    错误请求类： AccessToken错误
    """
    description = gettext('AccessToken in OSr-RestToken is invalid')


class OsrTokenError(Unauthorized):
    """
    错误请求类： CSRFToken或者AccessToken未提供或者异常
    """
    description = gettext('OSR-RestToken validation failed.')
