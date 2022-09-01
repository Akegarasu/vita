#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
DB_CONFIG = {
    "redis": {
        "host": [
            "127.0.0.1"
        ],
        "password": "<Your password>",
        "port": [
            "6379"
        ]
    },
    "mongodb": {
        "web": {
            "dbname": "osr_web",
            "password": "<Your password>",
            "config": {
                "fsync": False,
                "replica_set": None
            },
            "host": [
                "127.0.0.1:27017"
            ],
            "username": "root"
        },
        "user": {
            "dbname": "osr_user",
            "password": "<Your password>",
            "config": {
                "fsync": False,
                "replica_set": None
            },
            "host": [
                "127.0.0.1:27017"
            ],
            "username": "root"
        },
        "sys": {
            "dbname": "osr_sys",
            "password": "<Your password>",
            "config": {
                "fsync": False,
                "replica_set": None
            },
            "host": [
                "127.0.0.1:27017"
            ],
            "username": "root"
        }
    }
}