#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import time
import datetime


def time_to_utcdate(time_stamp=None, tformat="%Y%m%d"):
    """
    Timestamp to UTC date
    :param time_stamp:
    :param tformat:
    :return:
    """
    # If the default parameters in parameters using time, Time will not change
    if not time_stamp:
        time_stamp = time.time()
    utcdate = datetime.datetime.utcfromtimestamp(time_stamp).strftime(tformat)
    if utcdate.isdigit():
        return int(utcdate)
    else:
        return utcdate


def date_to_time(date, tformat="%Y%m%d"):
    """
    Date to Timestamp
    :param date:
    :param tformat:
    :return:
    """
    utc = time.mktime(datetime.datetime.utcnow().timetuple())
    local = time.mktime(datetime.datetime.now().timetuple())
    jet_lag = (local - utc) // 3600
    if not isinstance(date, str):
        date = str(int(date))
    time_stamp = time.mktime(
        datetime.datetime.strptime(
            date, tformat).timetuple())
    time_stamp += 3600 * jet_lag
    return time_stamp
