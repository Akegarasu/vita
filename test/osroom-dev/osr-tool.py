#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import getopt
import sys
from apps.configs.sys_config import PROJECT_PATH


def main():
    """
    脚本主函数
    :return:
    """
    from tools.usage import usage_help
    s_ops = "hy"
    s_opexplain = [
        "help",
        "Yes, Valid only when using --up-pylib"
    ]
    l_ops = ["up-pylib", "venv-path=", "latest", "up-conf-sample", "add-user"]
    l_opexplain = [
        "<value>, Update python package (dependent package)",
        "<value>, up-pylib input venv path: <venv-path> or null",
        "up-pylib Update to the latest version",
        "Update to the latest package",
        "Update the system configuration sample file."
        "Automatically remove sensitive data (eg passwords)\n"
        "Mainly the following configuration files:\n"
        " {}/apps/config_sample.py;\n"
        " {}/apps/db_config_sample.py".format(
            PROJECT_PATH, PROJECT_PATH),

        "Add a Root user, generally only used to initialize the user when the site was just created"
    ]

    action = ["Update python lib: python {} --up-pylib".format(__file__),
              "Update config sample: python {} --up-conf-sample".format(
                  __file__),
              "Add user: python {} --add-user".format(__file__)
              ]

    opts, args = getopt.getopt(sys.argv[1:], s_ops, l_ops)
    is_up_pylib = False
    is_yes = False
    venv_path = "default"
    latest = False
    for op, value in opts:
        if op == "--up-pylib":
            is_up_pylib = True
        elif op == "--venv-path":
            venv_path = value
        elif op == "--latest":
            latest = True

        elif op == "--up-conf-sample":
            from apps.core.utils.sys_tool import copy_config_to_sample
            copy_config_to_sample()

        elif op == "--add-user":
            from start import mdbs
            from apps.core.utils.sys_tool import add_user
            add_user(mdbs=mdbs)
        elif op == "-y":
            is_yes = True
        elif op == "-h" or op == "--help":
            usage_help(s_ops, s_opexplain, l_ops, l_opexplain, action=action)

    if is_up_pylib:
        from apps.core.utils.sys_tool import update_pylib
        update_pylib(venv_path=venv_path, latest=latest, is_yes=is_yes)
    if not opts:
        usage_help(s_ops, s_opexplain, l_ops, l_opexplain, action=action)


if __name__ == '__main__':
    main()
