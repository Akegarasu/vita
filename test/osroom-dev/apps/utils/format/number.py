#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo


def get_num_digits(num):
    n = 0
    while True:
        if not num:
            break
        n += 1
        num = int(num) >> 1
    return n
