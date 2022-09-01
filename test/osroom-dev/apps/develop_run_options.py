#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2020/03/12 19:37
# @Author : Allen Woo
import os
import sys
import click
from apps.app import app
from apps.configs.sys_config import PROJECT_PATH
from asnyc_task_start import async_task_worker


@app.cli.command()
@click.option('-h', '--host', default="127.0.0.1",
              help='The interface to bind to.')
@click.option('-p', '--port', default=5000,
              help='The port to bind to.')
@click.option('--debug/--no-debug', default=False,
              help='Enable or disable the debugger. By default'
                   ' the debugger is active if debug is enabled.')
@click.option('--reload/--no-reload',
              help='Enable or disable the reloader. '
                   'By default the reloader is active if debug is enabled.')
@click.option('-dt/<Not to use>',
              help='En:Disable client Token authentication.'
                   'By default the enable token. '
                   'Cn: 禁止客户端Token验证，默认是开启验证的')
@click.option('--cert', type=click.Path(exists=True),
              help='Specify a certificate file to use HTTPS.')
@click.option('--key',  type=click.File(),
              help='The key file to use when specifying a certificate.')
@click.option('--eager-loading/--lazy-loader',
              help='Enable or disable eager loading. By default '
                   'eager loading is enabled if the reloader is disabled.')
@click.option('--with-threads/--without-threads',
              help='Enable or disable multithreading.')
def run_osroom(**kwargs):
    """
    CN: 运行osroom 本地开发Server(基于flask run)

    flask run 命令不能满足osroom开发环境需求(如: 实现客户端验证开关-dt).

    所以写了run-osroom命令处理，在其内部执行flask run.

    你应该使用run-osroom来启动开发服务, run-osroom会提前启动osroom的异步任务程序

    $ flask run-osroom

    """
    # flask run命令不能满足当前开发环境需求，所以使用run-osroom命令先处理，内部执行flask run
    # 如: 实现命令行开关flask run 的debugger
    print(" * Run osroom")
    sys_argv = list(sys.argv)[2:]
    parameter_processing(sys_argv=sys_argv, op="write")
    del_ops = ["-dt"]
    for del_op in del_ops:
        if del_op in sys_argv:
            sys_argv.remove(del_op)

    if kwargs.get("debugger") or kwargs.get("debug"):
        os.putenv("FLASK_ENV", "development")
    else:
        os.unsetenv("FLASK_ENV")

    """
    开发环境下直接启动异步任务启动
    注意: 开发环境下的celery启动不要在flask run下面开子进程启动，因为会出现端口占用异常
    """
    async_task_worker()

    # 从Flask 0.11版本开始，官方就建议使用flask run命令来取代app.run()
    # 当时flask run的参数不能满足osroom， 所以就改成使用 run-osroom来启动
    start_info_print(" * Flask server run")
    if "--debug" in sys_argv:
        sys_argv[sys_argv.index("--debug")] = "--debugger"
    flask_server = "flask run {}".format(" ".join(sys_argv))
    os.system(flask_server)


def parameter_processing(sys_argv, op):
    """
    额外的特殊参数处理
    :param sys_argv:
    :return:
    """
    result = {
        "is_debug": True,
        "csrf_enabled": True
    }
    if op == "write":
        sys_argv_str = " ".join(list(sys_argv))
        with open("{}/.temp_option".format(PROJECT_PATH), 'w') as wf:
            wf.write(sys_argv_str)
        return
    else:
        result["is_debug"] = app.debug
        with open("{}/.temp_option".format(PROJECT_PATH)) as rf:
            sys_argv = rf.read()
            sys_argv = sys_argv.split(" ")
        if "-dt" in sys_argv:
            result["csrf_enabled"] = False
    return result


def start_info_print(msg):
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN'):
        # 未启用debug或者启用之后的主程序
        print(msg)
