#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import logging
import logging.config
import os
import time
import traceback
from uuid import uuid1

from flask import g, request
from flask_login import current_user

from apps.configs.sys_config import LOG_FORMATTER, LOG_PATH, \
    WEBLOG_EXCEP_FILENAME, WEBLOG_EXCEP_LEVEL, WEBLOG_NORMAL_FILENAME, \
    WEBLOG_NORMAL_LEVEL, WEBLOG_START_FILENAME
from apps.core.logger.logger_server import LoggerClientUDP


class WebLogger:

    def __init__(self):
        self.set_logger = LoggerClientUDP()

    def init_app(self, app):

        filename = os.path.abspath("{}/{}".format(LOG_PATH, WEBLOG_NORMAL_FILENAME))
        normal_log = LoggerClientUDP(set_level=WEBLOG_NORMAL_LEVEL,
                                     logfile=filename,
                                     get_log_name='web_normal',
                                     formatter=LOG_FORMATTER)

        filename = os.path.abspath("{}/{}".format(LOG_PATH, WEBLOG_EXCEP_FILENAME))
        error_log = LoggerClientUDP(set_level=WEBLOG_EXCEP_LEVEL,
                                    logfile=filename,
                                    get_log_name='web_error',
                                    formatter=LOG_FORMATTER)

        @app.before_request
        def before_request_log():
            """
            DEFORE REQUEST
            :return:
            """

            global _weblog_g
            _weblog_g = {"log": {}}
            st = time.time()
            # "{}{}".format(st, randint(1, 1000000))
            _weblog_g["log"]['request_id'] = uuid1()
            g.weblog_id = _weblog_g["log"]['request_id']
            _weblog_g["log"]['st'] = st
            _weblog_g["log"]['ip'] = request.remote_addr
            _weblog_g["log"]['url'] = request.url

            if current_user.is_authenticated:
                _weblog_g["log"]['user_id'] = current_user.str_id

        @app.teardown_request
        def teardown_request_log(exception):
            """
            Teardown request
            :param exception:
            :return:
            """

            try:
                _weblog_g["log"]["method"] = request.c_method
                _weblog_g["log"]['u_t_m'] = "{} ms".format(
                    (time.time() - _weblog_g["log"]['st']) * 1000)
                normal_log.info("[api|view] {}".format(_weblog_g["log"]))
                if exception:
                    error_log.error(_weblog_g["log"])
                    error_log.exception(exception)
            except Exception:
                _weblogger_error = {
                    "type": "weblogger error",
                    "exceptione": traceback.format_exc()
                }
                error_log.error(_weblogger_error)

    def start_log(self):
        """
        :return: logger obj
        """

        filename = os.path.abspath(
            "{}/{}".format(LOG_PATH, WEBLOG_START_FILENAME))
        sys_start_log = LoggerClientUDP(
            set_level=logging.INFO,
            logfile=filename,
            get_log_name='sys_start',
            formatter=LOG_FORMATTER)
        return sys_start_log


web_start_log = WebLogger().start_log()
