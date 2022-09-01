#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2020/03/09 15:04
# @Author : Allen Woo


class SpecialChars:
    
    def db_regex_special_chars(self):
        regular_special_chars = {}
        for i in range(33, 47):
            char = chr(i)
            regular_special_chars[char] = "\{}".format(char)
        for i in range(58, 65):
            char = chr(i)
            regular_special_chars[char] = "\{}".format(char)
        for i in range(93, 95):
            char = chr(i)
            regular_special_chars[char] = "\{}".format(char)
        for i in range(123, 127):
            char = chr(i)
            regular_special_chars[char] = "\{}".format(char)
        regular_special_chars = dict(
            regular_special_chars,
            **{
                "[": "\[",
                ":": "\:",
                "~": "\~"
            }
        )
        return regular_special_chars