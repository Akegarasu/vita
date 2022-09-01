#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import getopt
import os
import sys
current_path = os.path.abspath(os.path.dirname(__file__))
project_path = os.path.abspath("{}/../..".format(current_path))
sys.path.append(project_path)
from tools.usage import usage_help


class Transations:

    def main(self):

        self.cfg_path = "{}/babel.cfg".format(current_path)
        self.extract_path = "{}/apps".format(project_path)
        s_ops = "hqo:"
        l_ops = [
            "init",
            "update",
            "compile",
            "cfg=",
            "ext=",
            "lan=",
            "all-lan"]
        s_opexplain = [
            "help",
            "quiet:A small amount of output",
            "<output directory>, Output directory.Optional: admin_pages, python-pg, theme",
        ]
        l_opexplain = [
            "init translation(初始化翻译)",
            "Update: Extract and update(用于更新,提取最新的需翻译文本)",
            "compile(更新并翻译后,需要发布翻译)",
            "<cfg file path>, The default:{}(只提取html,js文件)."
            "\nOptional: {}/babel_py.cfg(只提取py文件)".format(
                self.cfg_path,
                current_path),
            "<Extract path>, \nSuch as: {}"
            "\n{}/theme".format(
                self.extract_path,
                self.extract_path),
            "<language>, Default:zh_Hans_CN  Optional: zh_CN,zh_Hans_CN,en_GB",
            "View all languages"]

        action = [
            "init, [--init --ext <path> -o <dir name> --lan en_US]",
            "update, [--update --ext <path> -o <dir name> --cfg <cfg file path>]",
            "compile, [--compile -o <dir name>]",
            """Eg:
Ext theme text:
--update --ext apps/themes -o theme --lan en_US\n
Ext admin pages text:
--update --ext apps/admin_pages -o admin_pages --lan en_US\n
Ext python:
--update --ext apps -o python-pg --cfg tools/translations/babel_py.cfg --lan zh_Hans_CN\n
Theme Tr compile:
--compile -o theme\n
Admin pages Tr compile:
--compile -o admin_pages\n
Python Tr compile:
--compile -o python-pg
"""
        ]

        opts, args = getopt.getopt(sys.argv[1:], s_ops, l_ops)
        func = None
        self.save_path = None
        self.quiet = ""
        self.lan = "zh_Hans_CN"

        if not opts:
            usage_help(s_ops, s_opexplain, l_ops, l_opexplain, action=action)
        for op, value in opts:
            if op == "-q":
                self.quiet = "-q"
            elif op == "--lan":
                self.lan = value.strip()
            elif op == "--all-lan":
                os.system("pybabel --list-locales")
                sys.exit()

            elif op == "--cfg":
                self.cfg_path = value.strip()

            elif op == "--ext":
                self.extract_path = value.rstrip("/")

            elif op == "-o":
                self.save_path = "{}/apps/translations/{}".format(project_path, value.strip("/"))

            elif op == "--init":
                func = self.init_tr

            elif op == "--update":
                func = self.update_tr

            elif op == "--compile":
                func = self.compile_tr

            elif op == "-h" or op == "--help":
                usage_help(
                    s_ops,
                    s_opexplain,
                    l_ops,
                    l_opexplain,
                    action=action)

        print(self.save_path)
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        func()

    def init_tr(self):
        """
        compile transations
        """
        self.cfg_sack()

        if not self.quiet:
            self.redirect = ""
        if self.lan:
            print("Extract...")
            print(self.extract_path)
            os.system('pybabel {} extract -F {} -o {}/messages.pot {}'.format(
                self.quiet, self.cfg_path, self.save_path, self.extract_path))
            print("Init...")
            os.system('pybabel {} init -i {}/messages.pot -d {} -l {}'.format(self.quiet,
                                                                              self.save_path,
                                                                              self.save_path,
                                                                              self.lan))
            self.print_cfg()
            print("Success")
        else:
            print("You need to specify the language:--lan <language>\n")

    def update_tr(self):
        """
        update transations
        """

        self.cfg_sack()

        lc_msg_path = "{}/{}/LC_MESSAGES".format(self.save_path, self.lan)
        po_filepath = os.path.join(lc_msg_path, "messages.po")
        if not os.path.exists(po_filepath):
            print(po_filepath)
            raise Exception(
                "Missing messages.po file, please reinitialize translation. -h")
        if not self.quiet:
            self.redirect = ""

        os.system(
            'pybabel {} extract -F {} -k lazy_gettext -o {}/messages.pot {}'.format(
                self.quiet,
                self.cfg_path,
                self.save_path,
                self.extract_path))

        os.system(
            'pybabel {} update -i {}/messages.pot -d {}'.format(
                self.quiet,
                self.save_path,
                self.save_path
            ))

        self.print_cfg()
        print("Success")

    def compile_tr(self):
        """
        compile transations
        """

        if not self.quiet:
            self.redirect = ""
        os.system('pybabel compile -d {} {}'.format(self.save_path, self.redirect))

    def cfg_sack(self):

        print("cfg file: " + self.cfg_path)
        self.print_cfg()
        ch = input("Are you sure you want to use this cfg file?(Y/N): ")
        if ch.lower() not in ["yes", "y"]:
            sys.exit(0)

    def print_cfg(self):

        with open(self.cfg_path) as rf:
            print(
                "* Extract content type[{}]:".format(os.path.split(self.cfg_path)[-1]))
            for line in rf.readlines():
                print("    " + line.strip("\n"))


if __name__ == '__main__':

    trs = Transations()
    trs.main()
