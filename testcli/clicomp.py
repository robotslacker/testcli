# -*- coding: utf-8 -*-
import sys
import click
import platform
import signal
from .__init__ import __version__


# 信号处理程序
def abortSignalHandler(signum, frame):
    click.secho("Got signal [" + str(signum) + "]. Quit application.", err=True, fg="red")
    if frame:
        pass
    # 直接退出
    sys.exit(255)


@click.command()
@click.option("--version", is_flag=True, help="Show TestCli version.")
@click.option("--reference", type=str, help="Specify the log file for reference.",)
@click.option("--logfile", type=str, help="Specify the log file for comparison.",)
@click.option("--rule", type=str, help="Compare rule file.")
@click.option("--output", type=str, help="Specify the result output file.")
@click.option("--outputformat", type=str, default = "PLAIN", help="Specify the result output file format  PLAIN|HTML.")
def cli(
        version,
        reference,
        logfile,
        rule,
        output,
        outputformat
):
    # 捕捉信号，处理服务中断的情况
    if platform.system().upper() in ["LINUX", "DARWIN"]:
        # 通信管道中断，不处理中断信息，放弃后续数据
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        # 被操作系统KILL
        signal.signal(signal.SIGTERM, abortSignalHandler)

    # 打印版本信息
    if version:
        click.secho("Version: " + __version__)
        sys.exit(0)

    # 判断报告输出格式
    if outputformat not in ["PLAIN", "HTML"]:
        click.secho("Compare tool only support PLAIN(text mode) or HTML(html mode). ", err=True, fg="red")
        sys.exit(255)

    # 解析比较配置文件

    print("Hello World. TODO.")


# 主程序
if __name__ == "__main__":
    cli()
