#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask_babel import Babel
# from flask_oauthlib.client import OAuth
from celery import Celery

from apps.configs.celery_config import CeleryConfig
from apps.core.db.redis_conn import Myredis
from apps.core.flask.myflask import OsrApp
from apps.core.flask.cache import Cache
from apps.core.flask.rest_session import RestSession
from apps.core.db.mongodb import MyMongo
from flask_mail import Mail
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from apps.configs.db_config import DB_CONFIG

"""
 Flask app 与其他核心模块实例化
 注意: 不要将模块初始话设置放在本文件
"""
# 主程序
app = OsrApp(__name__)
mdbs = {}
for k in DB_CONFIG["mongodb"].keys():
    mdbs[k] = MyMongo()

cache = Cache()
babel = Babel()
csrf = CSRFProtect()
login_manager = LoginManager()
sess = Session()
rest_session = RestSession()
mail = Mail()
# oauth = OAuth()
redis = Myredis(
    host=DB_CONFIG["redis"]["host"][0],
    port=DB_CONFIG["redis"]["port"][0],
    password=DB_CONFIG["redis"]["password"]
)

# Celery 配置
app.config.from_object(CeleryConfig)
celery = Celery(
    app.import_name,
    backend=app.config.get('BROKER_URL'),
    broker=app.config.get('BROKER_URL')
)

celery.conf.ONCE = {
  'backend': 'celery_once.backends.Redis',
  'settings': {
    'url': app.config.get('ONCE_BROKER_URL'),
    'default_timeout': 60 * 5
  }
}
