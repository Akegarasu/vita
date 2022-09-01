#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import json
import os
import socket
import time
import logging
from logging.handlers import TimedRotatingFileHandler

from apps.configs.sys_config import LOG_PATH, SOCKET_PORT
from apps.utils.osr_async.osr_async import async_process


class LoggerClientUDP:

    def __init__(self,
                 set_level=logging.INFO,
                 logfile="{}/{}.log".format(LOG_PATH, time.time()),
                 get_log_name='logger',
                 formatter='%(asctime)s %(levelname)s %(message)s',
                 **kwargs
                 ):
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.set = {
            "kwargs": {
                "set_level": set_level,
                "logfile": logfile,
                "get_log_name": get_log_name,
                "formatter": formatter
            }
        }
        self.sp = "__+++++udposrlog+++++__"

    def debug(self, log, **kwargs):
        self.set["log_level"] = "debug"
        self.send_log(log=log)

    def info(self, log, **kwargs):
        self.set["log_level"] = "info"
        self.send_log(log=log)

    def warning(self, log, **kwargs):
        self.set["log_level"] = "warning"
        self.send_log(log=log)

    def error(self, log, **kwargs):
        self.set["log_level"] = "error"
        self.send_log(log=log)

    def critical(self, log, **kwargs):
        self.set["log_level"] = "critical"
        self.send_log(log=log)

    def exception(self, log, **kwargs):
        self.set["log_level"] = "error"
        self.send_log(log=log)

    def send_log(self, log):
        set = json.dumps(self.set)
        log = "{}{}{}".format(set, self.sp, log)
        self.sk.sendto(log.encode(), ("127.0.0.1", SOCKET_PORT))

    def __del__(self):
        self.sk.close()


class LogServerUDP:

    def init_app(self):
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sk.bind(("127.0.0.1", SOCKET_PORT))
            self.failed = False
            print(" * [pid:{}] Logger Server...".format(os.getpid()))
        except:
            self.failed = True
            return False

        self.loggers = {}
        self.self_logfile = "{}/logger_server.log".format(LOG_PATH)
        self.get_log_name = "logger_server"
        self.kwargs = {
            "set_level": logging.DEBUG,
            "logfile": self.self_logfile,
            "get_log_name": self.get_log_name,
            "formatter": '%(asctime)s %(levelname)s %(message)s'
        }
        self.set_logger(self.kwargs)
        self.sp =  "__+++++udposrlog+++++__"
        return True

    def set_logger(self, kwargs):
        set_level = kwargs.get("set_level")
        logfile = kwargs.get("logfile")
        get_log_name = kwargs.get("get_log_name")
        formatter = kwargs.get("formatter")
        if not os.path.exists(os.path.split(logfile)[0]):
            os.makedirs(os.path.split(logfile)[0])
        # According to the time
        file_handler = TimedRotatingFileHandler(logfile, "midnight", 1, 7)
        file_handler.suffix = "%Y-%m-%d"
        # According to the size
        # file_handler = RotatingFileHandler(filename, maxBytes=10*1024*1024, backupCount=3)
        file_handler.setLevel(set_level)
        _formatter = logging.Formatter(formatter)
        file_handler.setFormatter(_formatter)
        logging.getLogger(get_log_name).addHandler(file_handler)
        logging.getLogger(get_log_name).setLevel(logging.INFO)
        logg = logging.getLogger(get_log_name)
        self.loggers[get_log_name] = {
            "critical": logg.critical,
            "error": logg.error,
            "warning": logg.warning,
            "info": logg.info,
            "debug": logg.debug,
        }
        return self.loggers[get_log_name]

    @async_process()
    def log_server(self):
        if self.failed:
            return
        while True:
            data = self.sk.recv(10240)
            data = data.decode()
            data = data.split(self.sp)
            sets = data[0]
            log = data[1]
            sets = json.loads(sets)
            kwargs = sets["kwargs"]
            logg = self.loggers.get(kwargs["get_log_name"])
            if not logg:
                logg = self.set_logger(kwargs)
            logg[sets["log_level"]](log)

    def __del__(self):
        self.sk.close()
