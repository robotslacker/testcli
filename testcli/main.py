# -*- coding: utf-8 -*-
import os
import sys
import traceback
import click
import pytest
import platform
import signal
from .__init__ import __version__
from .testcli import TestCli
from .testcliexception import TestCliException

# 定义全局变量，程序的返回值，默认是0
appExitValue = 0

# 主程序句柄
appHandler = None

@click.command()
@click.option("--version", is_flag=True, help="Show TestCli version.")
@click.option("--logon", type=str, help="SQL logon user name and password. user/pass",)
@click.option("--logfile", type=str, help="Log every command and its results to file.",)
@click.option("--execute", type=str, help="Execute command script.")
@click.option("--commandmap", type=str, help="Command mapping file.")
@click.option("--nologo", is_flag=True, help="Execute with no-logo mode.")
@click.option("--xlog", type=str, help="Save command extended log.")
@click.option("--xlogoverwrite", is_flag=True, help="Overwrite extended log if old file exists. Default is false")
@click.option("--clientcharset", type=str, help="Set client charset. Default is UTF-8.")
@click.option("--resultcharset", type=str, help="Set result charset. Default is same to clientCharset.")
@click.option("--profile", type=str, help="Startup profile.")
@click.option("--scripttimeout", type=int, help="Script timeout(seconds).")
@click.option("--namespace", type=str, help="Command default name space(SQL|API). Default is depend on file suffix.")
@click.option("--selftest", is_flag=True, help="Run self test and exit.")
@click.option("--suitename", type=str, help="Test suite name.")
@click.option("--casename", type=str, help="Test case name.")
def cli(
        version,
        logon,
        logfile,
        execute,
        commandmap,
        nologo,
        xlog,
        xlogoverwrite,
        clientcharset,
        resultcharset,
        profile,
        scripttimeout,
        namespace,
        selftest,
        suitename,
        casename
):
    if version:
        print("Version:", __version__)
        return

    # 程序自检
    if selftest:
        testpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "test", "testcliunittest.py"))
        pytest.main(
            args=[
                "-vs",
                testpath,
            ],
        )
        return

    # 程序脚本超时时间设置
    if not scripttimeout:
        scripttimeout = -1

    global  appHandler
    appHandler = TestCli(
        logfilename=logfile,
        logon=logon,
        script=execute,
        commandMap=commandmap,
        nologo=nologo,
        xlog=xlog,
        xlogoverwrite=xlogoverwrite,
        clientCharset=clientcharset,
        resultCharset=resultcharset,
        profile=profile,
        scripttimeout=scripttimeout,
        namespace=namespace,
        suitename=suitename,
        casename=casename
    )

    # 运行主程序
    global appExitValue
    appExitValue = appHandler.run_cli()


# 信号处理程序
def abortSignalHandler(signum, frame):
    click.secho("Got signal [" + str(signum) + "]. Quit application.", err=True, fg="red")
    if frame:
        pass
    # Cli会处理EOF Error，类似于直接退出
    raise EOFError


if __name__ == "__main__":

    # 捕捉信号，处理服务中断的情况
    if platform.system().upper() == "LINUX":
        signal.signal(signal.SIGTERM, abortSignalHandler)

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
