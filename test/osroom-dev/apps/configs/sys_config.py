#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import logging
import os
curren_path = os.path.abspath(os.path.dirname(__file__))

"""
#################################################
网站系统配置文件,不提供给管理端配置部分
#################################################
"""

"""
Osroom版本
"""
VERSION = "3.0 beta"

"""
  需要导入的模块
"""
MODULES = ["apps.modules.user.process.load_user_request"]

"""
 项目各路径配置PATH
"""
PROJECT_PATH = os.path.abspath("{}/../..".format(curren_path))
APPS_PATH = os.path.abspath("{}/apps".format(PROJECT_PATH))
STATIC_PATH = os.path.abspath("{}/static".format(APPS_PATH))

"""
插件管理配置
"""
PLUG_IN_FOLDER_NAME = "plugins"
PLUG_IN_FOLDER = "{}/{}".format(APPS_PATH, PLUG_IN_FOLDER_NAME)
# 插件包配置文件conf.yaml必须需要的参数
PLUG_IN_REQUIRED_CONF = [
    "startup_file_name",
    "hook_name",
    "alias_name",
    "introduce",
    "version",
    "license"]
# 插件配置缓存
PLUG_IN_CONFIG_CACHE_KEY = "web_get_plugin_config"

"""
 网页前端template
"""
ADMIN_TEMPLATE_FOLDER = "{}/admin_pages/pages".format(APPS_PATH)
THEME_TEMPLATE_FOLDER = "{}/themes".format(APPS_PATH)
STATIC_HTML_TEMPLATE_FOLDER = "{}/static_html_pages".format(APPS_PATH)
ADMIN_STATIC_FOLDER = "{}/admin_pages/static".format(APPS_PATH)
TEMP_STATIC_FOLDER = "{}/static/.temp".format(APPS_PATH)

# 主题包配置文件conf.yaml必须需要的参数
THEME_REQUIRED_CONF = [
    "theme_name",
    "cover_path",
    "introduce",
    "version",
    "license"]

"""
路由,不要以"/"结尾
"""
API_URL_PREFIX = "/api"
OPEN_API_URL_PREFIX = "/open-api"

ADMIN_URL_PREFIX = "/osr-admin"
STATIC_HTML_PAGE_PREFIX = "/st-html"
DEFAULT_ADMIN_LOGIN_PAGE = "/osr-admin/sign-in"

STATIC_URL_PREFIX = "/static"
ADMIN_STATIC_URL_PREFIX = "/admin-pages/static"


"""
 权限permission
"""

"""
 固定KEY的缓存配置
"""
# SecretToken缓存key与超时
REST_SECRET_TOKEN_CACHE_KEY = "web_secret_token"
REST_SECRET_TOKEN_CACHE_TIMEOUT = 3600 * 24

# config.py中的CONFIG缓存配置
CONFIG_CACHE_KEY = "web_get_config"
# 配置的缓存时间,主要是为了当你修改了CONFIG_CACHE_KEY后,老的配置缓存未清理，过期自动清理
CONFIG_CACHE_TIMEOUT = 3600 * 24  # 单位s

THEME_NAVS_CAHCE_KEY = "theme_navs_caches"

"""
 日志 log
"""
# weblog
SOCKET_PORT = 6005
LOG_PATH = "{}/logs".format(PROJECT_PATH)
WEBLOG_START_FILENAME = "site_start.log"
WEBLOG_NORMAL_FILENAME = "osroom.log"
WEBLOG_EXCEP_FILENAME = "error.log"
LOG_FORMATTER = "%(asctime)s %(levelname)s %(message)s"
WEBLOG_NORMAL_LEVEL = logging.DEBUG
WEBLOG_EXCEP_LEVEL = logging.INFO
# 如果为True则错误日志中不写入"详细的错误", 只写入错误类型
PRESERVE_CONTEXT_ON_EXCEPTION = False

"""
 Request
"""
# 不存在的请求警告
METHOD_WARNING = "405, The method is not allowed for the requested URL"

"""
 Babel
"""
# 多语言
BABEL_TRANSLATION_DIRECTORIES = "translations/admin_pages;translations/python-pg;translations/theme"

"""
第三方登录插件支持
"""
LOGIN_PLATFORM = [
    "wechat",
    "qq",
    "sina_weibo",
    "alipay",
    "github",
    "facebook",
    "twitter"]

"""
 针对浏览器访问的Session设置
"""

# 会话保护属性,strong或者basic
SESSION_PROTECTION = "strong"
SESSION_COOKIE_PATH = "/"
# 控制是否应该使用安全标志设置cookie
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False
# 设置参数SESSION_USE_SIGNER为True时,请保证session初始化前app.config中有SECRET_KEY
SESSION_USE_SIGNER = True

"""
 *安全
"""
# CSRF配置, 只对普通浏览器请求验证有效, 对使用RestToken验证的请求无效
WTF_CSRF_TIME_LIMIT = 3600 * 2
WTF_CSRF_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]

"""
其他
"""
# 默认字体路径, 用于生成验证码的
FONT_PATH = "{}/Arial.ttf".format(STATIC_PATH)
VIOLATION_IMG_PATH = "{}/sys_imgs/violation.png".format(STATIC_PATH)
# 最高权限位置
SUPER_PER = 0b11111111111111111111111111111111111111111111111111111
# 必须保留权限
PRESERVE_PERS = ["GENERAL_USER", "ROOT", "ADMIN", "STAFF"]

# cache 固定key
GET_DEFAULT_SYS_PER_CACHE_KEY = "sys_permissions_default"
GET_ALL_PERS_CACHE_KEY = "sys_permissions"
