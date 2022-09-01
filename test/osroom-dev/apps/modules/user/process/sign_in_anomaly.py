#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo


class AbnormalLogin:

    def __init__(self, old_login_logs, current_log):
        self.old_login_logs = old_login_logs
        self.current_log = current_log

    def area(self):
        log_cnt = len(self.old_login_logs)
        dif_n = 0  # 不同的地址计数
        same_n = 0  # 相同的地址计数
        same_total = 0  # 相同地址总数
        is_normal = True
        # 从最后一个开始取
        for i in range(log_cnt - 1, -1, -1):
            geo = self.old_login_logs[i]["geo"]
            try:
                if self.current_log["subdivisions"]["name"] != geo["subdivisions"]["name"]:
                    # 当前区域和历史第i个不一样
                    dif_n += 1
                    if dif_n >= 2:
                        is_normal = False
                else:
                    same_total += 1
                    same_n += 1
                    if same_n >= 2:
                        is_normal = True
            except BaseException:
                pass

            if same_total >= log_cnt // 3:
                # 如果相同的地区占比大于等于log数的1/3, 计为正常
                is_normal = True

            if is_normal:
                return "normal"
            else:
                return "abnormal"
        # 无历史登录log, 默认为正常登录
        return "normal"
