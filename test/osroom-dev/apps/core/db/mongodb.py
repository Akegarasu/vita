#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from pymongo import MongoClient
from pymongo.errors import AutoReconnect
from retrying import retry
from apps.core.utils.special_chars import SpecialChars


def retry_if_auto_reconnect_error(exception):
    return isinstance(exception, AutoReconnect)


class MyMongo:

    def __init__(self, app=None, config_prefix='MONGO', db_config=None):
        self.config = None
        self.connection = None
        self.name = ""
        self.db_conn = None
        self.db = None
        self.dbs = {}
        self.pymongo = None
        if app or db_config:
            self.init_app(app, config_prefix, db_config)

    def init_app(self, app=None, config_prefix='MONGO', db_config=None):

        self.pymongo = PyMongo(
            app=app,
            config_prefix=config_prefix,
            db_config=db_config
        )
        # DB
        self.dbs = {}
        self.db = self.pymongo.db
        self.db.__dict__["name"] = self.pymongo.name
        self.name = self.pymongo.name
        self.db.__dict__["name"] = self.name
        self.collection_names = self.pymongo.collection_names
        if len(self.collection_names):
            coll_ops = []
            ops = dir(self.pymongo.db_conn[self.collection_names[0]])
            for op in ops:
                if op[0] == "_":
                    continue
                coll_ops.append(op)
                for collection in self.collection_names:
                    umio = MdbOp()
                    umio.init_app(
                        self.pymongo.name,
                        collection,
                        self.pymongo.db_conn[collection],
                        op
                    )
                    self.db.__dict__[collection].__dict__[op] = umio.db_op
            self.dbs = MongoCollDict(
                self.pymongo,
                coll_ops
            )
        else:
            self.dbs = MongoCollDict(
                self.pymongo,
                []
            )
        for collection in self.collection_names:
            self.dbs[collection] = getattr(self.db, collection)
        for op in dir(self.pymongo.db_conn):
            if op[0] == "_":
                continue
            setattr(self.db, op, getattr(self.pymongo.db_conn, op))
        self.connection = self.pymongo.connection

    def close(self):
        self.pymongo.close()


class MongoCollDict(dict):

    def __init__(self, pymongo, coll_ops, *args):
        super().__init__(*args)
        self.counter = 0
        self.pymongo = pymongo
        self.coll_ops = coll_ops
        for op in dir(self.pymongo.db_conn):
            if op[0] == "_":
                continue
            setattr(self, op, getattr(self.pymongo.db_conn, op))

    def __getitem__(self, key):
        self.counter += 1
        if key not in self.keys():
            self.try_create_collection(key)
        return super(MongoCollDict, self).__getitem__(key)

    def try_create_collection(self, collection_name):
        self.create_collection(collection_name)
        self.__init_collection(collection_name)

    def __init_collection(self, collection_name):

        self[collection_name] = self.pymongo.db_conn[collection_name]
        for op in self.coll_ops:
            umio = MdbOp()
            umio.init_app(
                self.pymongo.name,
                collection_name,
                self.pymongo.db_conn[collection_name],
                op
            )
            self[collection_name].__dict__[op] = umio.db_op


class MdbOp:

    def __init__(self, **kargs):
        self.dbname = None
        self.collection_name = None
        self.db_coll = None
        self.operation = None
        special_chars = SpecialChars()
        self.regex_special_chars = special_chars.db_regex_special_chars()

    def init_app(self, db_name, collection_name, db_coll, operation):
        self.dbname = db_name
        self.collection_name = collection_name
        self.db_coll = db_coll
        self.operation = operation

    def retry_if_auto_reconnect_error(exception):
        """
        Return True if we should retry (in this case when it's an AutoReconnect),
         False otherwise
        """
        return isinstance(exception, AutoReconnect)

    @retry(retry_on_exception=retry_if_auto_reconnect_error,
           stop_max_attempt_number=2, wait_fixed=2000)
    def db_op(self, *args, **kwargs):
        self.regex_find_escape(args[0], **kwargs)
        if "regular_escape" in kwargs:
            del kwargs["regular_escape"]
        r = getattr(self.db_coll, self.operation)(*args, **kwargs)
        return r

    def regex_find_escape(self, filter_dict, **kwargs):
        if not kwargs.get("regular_escape", True):
            return filter_dict
        if isinstance(filter_dict, dict):
            for k, v in filter_dict.items():
                if k == "$regex":
                    filter_dict[k] = self.str_replace(v, self.regex_special_chars)
                elif isinstance(v, (dict, list, tuple)):
                    filter_dict[k] = self.regex_find_escape(v, **kwargs)
        else:
            for i, sub_filter in enumerate(filter_dict):
                if isinstance(sub_filter, dict):
                    for k, v in sub_filter.items():
                        if k == "$regex":
                            sub_filter[k] = self.str_replace(v, self.regex_special_chars)
                        elif isinstance(v, (dict, list, tuple)):
                            sub_filter[k] = self.regex_find_escape(v, **kwargs)
                    filter_dict[i] = sub_filter
                elif isinstance(sub_filter, (list, tuple)):
                    filter_dict[i] = self.regex_find_escape(sub_filter, **kwargs)
        return filter_dict

    def str_replace(self, content, chars_dict):
        content = content.replace("\\", "\\\\")
        for ch, rp_ch in chars_dict.items():
            content = content.replace(ch, rp_ch)
        return content


class PyMongo:

    """
    mondodb 数据库链接初始化类
    """

    def __init__(self, app=None, config_prefix='MONGO', db_config=None):
        self.config = None
        self.connection = None
        self.name = ""
        self.db_conn = None
        self.db = None
        if app or db_config:
            self.init_app(app, config_prefix, db_config)

    def init_app(self, app=None, config_prefix='MONGO', db_config=None):
        """
        初始化数据库库连接模块
        :param app:
        :param config_prefix:
        :param db_config:
        :return:
        """
        if not app and not db_config:
            raise Exception("Parameter: app or db_config must provide one")
        if app:
            def key(suffix):
                return '%s_%s' % (config_prefix, suffix)
            if key('URI') in app.config:
                self.config = app.config[key('URI')]
            else:
                raise Exception("{} is not in the database configuration file".format(key('URI')))

        elif db_config:
            self.config = db_config

        if self.config['replica_set']:
            self.connection = MongoClient(
                self.config['mongodb'],
                fsync=self.config['fsync'],
                read_preference=self.config['read_preference'],
                replicaSet=self.config['replica_set']
            )
        else:
            self.connection = MongoClient(
                self.config['mongodb'],
                fsync=self.config['fsync'],
                read_preference=self.config['read_preference'],
            )
        self.name = self.config['db']
        self.db_conn = self.connection[self.config['db']]
        self.collection_names = self.db_conn.collection_names()
        self.db = MongoCollection(
            self.db_conn,
            self.collection_names
        )

    def close(self):
        self.connection.close()

    def __del__(self):
        self.close()


class MongoCollection:

    def __init__(self, conn_db=None, collection_names=[]):
        self.collection_names = collection_names
        if conn_db:
            self.collection_object(conn_db)

    def collection_object(self, conn_db):

        for collection in self.collection_names:
            self.__dict__[collection] = conn_db[collection]
