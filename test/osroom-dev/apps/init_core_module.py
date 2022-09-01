#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import time
import os
from apps.core.db.config_mdb import DatabaseConfig
from apps.core.logger.logger_server import LogServerUDP
from apps.core.logger.web_logging import web_start_log, WebLogger
from apps.configs.config import CONFIG, SYS_CONFIG_VERSION
from apps.develop_run_options import start_info_print
from apps.utils.format.obj_format import ConfDictToClass
from apps.app import login_manager, redis, sess, cache, csrf, babel, \
    mdbs, mail, rest_session, celery
from apps.configs.sys_config import CONFIG_CACHE_KEY, BABEL_TRANSLATION_DIRECTORIES, \
    SESSION_PROTECTION, SESSION_COOKIE_PATH, SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SECURE, \
    WTF_CSRF_METHODS, SESSION_USE_SIGNER, PRESERVE_CONTEXT_ON_EXCEPTION, PLUG_IN_CONFIG_CACHE_KEY, \
    TEMP_STATIC_FOLDER

"""
初始化一些核心模块
"""


def init_core_module(app, **kwargs):
    """
    初始化核心模块
    :param app:
    :return:
    """
    csrf_enabled = kwargs.get("csrf_enabled")
    is_debug = kwargs.get("is_debug")
    # app config
    web_start_log.info("Initialize the core module")

    # 系统必要配置, 优先导入
    app.config.from_object(ConfDictToClass(CONFIG["system"], key="value"))
    app.config.from_object(ConfDictToClass(CONFIG["key"], key="value"))

    # 数据库
    redis.init_app()

    app.config.from_object(DatabaseConfig())
    for name, mdb in mdbs.items():
        mdb.init_app(app, config_prefix=name.upper())

    # 缓存
    app.config.from_object(ConfDictToClass(CONFIG["cache"], key="value"))
    app.config["CACHE_REDIS"] = redis
    app.config["CACHE_MONGODB_DBS"] = mdbs["sys"].dbs
    cache.init_app(app)

    # Clear CONFIG cache
    if not is_debug:
        version_info = mdbs["sys"].db.sys_config.find_one(
            {
                "new_version": {
                    "$exists": True
                }
            }
        )
        ago_time = time.time() - 3600 * 24
        ago_time_30m = time.time()-1800
        if version_info["sys_version_of_config"] >= SYS_CONFIG_VERSION \
                and version_info["update_time"] > ago_time \
                and version_info["update_time"] < ago_time_30m:
            # 系统正在使用的SYS_CONFIG_VERSION版本和当前机器CONFIG的一样，或更高
            # And: 配置24小时内已有更新
            # So: 这次不更新
            msg = " * [sys configs cache]  Not clean cache." \
                  " The system is using the same or higher configuration version.\n" \
                  "   And it was executed within 24 hours."
            start_info_print("\033[33m{}\033[0m".format(msg))
            web_start_log.warning(msg)
        else:
            with app.app_context():
                msg = " * Clean configuration cache successfully"
                cache.delete(CONFIG_CACHE_KEY)
                cache.delete(PLUG_IN_CONFIG_CACHE_KEY)
                web_start_log.info(msg)
                start_info_print(msg)

    # 异常错误信息
    app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = PRESERVE_CONTEXT_ON_EXCEPTION

    ###################################################
    # 在此之前, 任何程序不能调用utils.get_config.py下的方法
    ###################################################

    from apps.core.utils.get_config import get_configs, get_config
    from apps.core.flask.request import OsrRequestProcess
    from apps.core.flask.errorhandler import ErrorHandler
    from apps.core.blueprint import api, admin_view, theme_view, static_html_view, \
        static, open_api, admin_static_file
    from apps.core.flask.routing import RegexConverter
    from apps.core.flask.routing import push_url_to_db

    # 最大请求大小
    app.config["MAX_CONTENT_LENGTH"] = get_config(
        "system", "MAX_CONTENT_LENGTH") * 1024 * 1024
    # Session会话配置
    session_config = get_configs("session")
    session_config["SESSION_PROTECTION"] = SESSION_PROTECTION
    session_config["SESSION_COOKIE_PATH"] = SESSION_COOKIE_PATH
    session_config["SESSION_COOKIE_HTTPONLY"] = SESSION_COOKIE_HTTPONLY
    session_config["SESSION_COOKIE_SECURE"] = SESSION_COOKIE_SECURE
    session_config["SESSION_USE_SIGNER"] = SESSION_USE_SIGNER
    session_config["SESSION_MONGODB_DB"] = mdbs["sys"].name

    app.config.from_object(ConfDictToClass(session_config))
    app.config["SESSION_REDIS"] = redis
    app.config["SESSION_MONGODB"] = mdbs["sys"].connection
    sess.init_app(app)
    rest_session.init_app(app)

    # 邮件
    app.config.from_object(ConfDictToClass(get_configs("email")))
    mail.init_app(app)

    # Csrf token
    csrf_config = {}
    if csrf_enabled:
        csrf_config["CLIENT_TOKEN_AUTH_ENABLED"] = True
        start_info_print(" * Security authentication is turned on")
    else:
        csrf_config["CLIENT_TOKEN_AUTH_ENABLED"] = False
        start_info_print("\033[31m   WARNING: security verification is turned off\033[0m")

    # 这两个csrf参数这里关闭，request程序会根据CLIENT_TOKEN_AUTH_ENABLED判断处理
    csrf_config["WTF_CSRF_CHECK_DEFAULT"] = False
    csrf_config["CSRF_ENABLED"] = False

    csrf_config["WTF_CSRF_METHODS"] = WTF_CSRF_METHODS
    app.config.from_object(ConfDictToClass(csrf_config))
    csrf.init_app(app)

    # Babel
    app.config.from_object(ConfDictToClass(get_configs("babel")))
    app.config["BABEL_TRANSLATION_DIRECTORIES"] = BABEL_TRANSLATION_DIRECTORIES
    babel.init_app(app)

    # 登录管理
    login_manager.init_app(app)
    # login_manager.anonymous_user = AnonymousUser()
    login_manager.session_protection = SESSION_PROTECTION
    # oauth.init_app(app)
    # 让路由支持正则
    app.url_map.converters['regex'] = RegexConverter

    # 注册蓝图 blueprint
    web_start_log.info("Register blueprint, Initialize the routing")
    app.register_blueprint(api)
    app.register_blueprint(open_api)
    app.register_blueprint(admin_view)
    app.register_blueprint(theme_view)
    app.register_blueprint(static_html_view)
    app.register_blueprint(static)
    app.register_blueprint(admin_static_file)
    if not is_debug:
        st = time.time()
        push_url_to_db(app)
        start_info_print(" * Routing updates saved in the database. It tasks time {} sec".format(
            int(time.time() - st)
            )
        )

    celery.conf.update(app.config)
    # 请求处理
    request_process = OsrRequestProcess()
    request_process.init_request_process(app=app)
    request_process.init_babel_locale_selector(babel=babel)

    # 错误处理
    ErrorHandler(app)

    # Logger
    # Other
    log_udp = LogServerUDP()
    r = log_udp.init_app()
    if r:
        log_udp.log_server()
    weblog = WebLogger()
    weblog.init_app(app)
    if not os.path.exists(TEMP_STATIC_FOLDER):
        os.makedirs(TEMP_STATIC_FOLDER)
