#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo


def datas_paging(pre=10, page_num=1, data_cnt=0, datas=[]):
    """
    分页函数
    :param pre:
    :param page_num:
    :param data_cnt:
    :param datas:
    :return:
    """

    result = {}
    result['datas'] = datas
    if data_cnt % pre == 0:
        page_total = data_cnt // pre
    else:
        page_total = data_cnt // pre + 1
    current_page = page_num
    return {
        "datas": datas,
        "page_total": page_total,
        "current_page": current_page,
        "data_total": data_cnt}
