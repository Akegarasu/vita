#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo

import sys


def usage_help(short_ops, short_opexplain, long_ops=[], long_opexplain=[], usage=[], action=[]):
    if usage:
        print("Usage:")
        for u in usage:
            print("\t{}".format(u))

    print("[option]:")
    s_op = short_ops.strip(":").split(":")
    i = 0
    for v in s_op:
        if len(v) != 1:
            v2_n = 0
            for v2 in v:
                print("\t-{}: {}".format(v2, short_opexplain[v2_n + i].replace("\n", "\n\t\t")))
                v2_n += 1
            i += len(v)
        else:
            print("\t-{}: {}".format(v, short_opexplain[i].replace("\n", "\n\t\t")))
            i += 1
    # long
    for i in range(0, len(long_ops)):
        print("\t--{}: {}".format(
            long_ops[i].strip("="),
            long_opexplain[i].replace("\n", "\n\t\t"))
        )

    if action:
        print("[action]:")
        for i, a in enumerate(action):
            print("\t{}: {}".format(i+1, a.replace("\n", "\n\t\t")))
    print("\n")
    sys.exit()
