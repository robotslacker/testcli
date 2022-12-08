# -*- coding: utf-8 -*-
import os
import sys
import traceback
import click
import pytest

from testcli.__init__ import __version__
from testcli.testcli import TestCli
from testcli.testcliexception import TestCliException

# 定义全局变量，程序的返回值，默认是0
appExitValue = 0


@click.command()
@click.option("--version", is_flag=True, help="Output TestCli version.")
@click.option("--logon", type=str, help="logon user name and password. user/pass",)
@click.option("--logfile", type=str, help="Log every query and its results to a file.",)
@click.option("--execute", type=str, help="Execute command script.")
@click.option("--commandmap", type=str, help="Command mapping file.")
@click.option("--nologo", is_flag=True, help="Execute with no-logo mode.")
@click.option("--xlog", type=str, help="Command extended log.")
@click.option("--syncdriver", is_flag=True, help="Download jdbc jar from file server.")
@click.option("--clientcharset", type=str, help="Set client charset. Default is UTF-8.")
@click.option("--resultcharset", type=str, help="Set result charset. Default is same to clientCharset.")
@click.option("--profile", type=str, help="Init profile.")
@click.option("--scripttimeout", type=int, help="Script Timeout(Seconds).")
@click.option("--namespace", type=str, help="Command name space.")
@click.option("--selftest", is_flag=True, help="Run self test.")
def cli(
        version,
        logon,
        logfile,
        execute,
        commandmap,
        nologo,
        xlog,
        syncdriver,
        clientcharset,
        resultcharset,
        profile,
        scripttimeout,
        namespace,
        selftest
):
    if version:
        print("Version:", __version__)
        return

    # 从服务器下下载程序需要的各种jar包
    if syncdriver:
        testcli = TestCli(
            logfilename=logfile,
            logon=logon,
            nologo=nologo
        )
        testcli.syncdriver()
        return

    # 程序自检
    if selftest:
        testpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "test", "testcliunittest.py"))
        pytest.main([testpath, ])
        return

    # 程序脚本超时时间设置
    if not scripttimeout:
        scripttimeout = -1

    testcli = TestCli(
        logfilename=logfile,
        logon=logon,
        script=execute,
        commandMap=commandmap,
        nologo=nologo,
        xlog=xlog,
        clientCharset=clientcharset,
        resultCharset=resultcharset,
        profile=profile,
        scripttimeout=scripttimeout,
        namespace=namespace
    )

    # 运行主程序
    global appExitValue
    appExitValue = testcli.run_cli()


if __name__ == "__main__":
    # 根据cli的结果退出，如果意外，退出返回值为255
    try:
        cli()
    except SystemExit as e:
        sys.exit(int(appExitValue))
    except TestCliException as se:
        click.secho(se.message, err=True, fg="red")
        sys.exit(255)
    except Exception as ge:
        if "TESTCLI_DEBUG" in os.environ:
            print('traceback.print_exc():\n%s' % traceback.print_exc())
            print('traceback.format_exc():\n%s' % traceback.format_exc())
        click.secho(repr(ge), err=True, fg="red")
        sys.exit(255)
