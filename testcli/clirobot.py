# -*- coding: utf-8 -*-
import os
import sys
import click
import platform
import signal
import logging
import coloredlogs
from .robot.common.runregress import Regress


# 信号处理程序
def abortSignalHandler(signum, frame):
    click.secho("Got signal [" + str(signum) + "]. Quit application.", err=True, fg="red")
    if frame:
        pass
    # 直接退出
    sys.exit(255)


@click.command()
@click.option("--job", type=str, required=True, help="Specify robot job file or directory.",)
@click.option("--work", type=str, required=True,
              help="Specify the work directory(ALL FILES IN THIS DIRECTORY WILL BE CLEANED).",)
@click.option("--parallel", type=int, default=1,
              help="Specify the parallelism of the jobs, default is 1, means no parallel.")
@click.option("--jobtimeout", type=int, default=-1,
              help="Specify the timeout limit of whole jobs, Default is -1, means no limit.")
@click.option("--workertimeout", type=int, default=-1,
              help="Specify the timeout limit of one job, Default is -1, means no limit.")
def cli(
        job,
        work,
        parallel,
        jobtimeout,
        workertimeout
):
    # 捕捉信号，处理服务中断的情况
    if platform.system().upper() in ["LINUX", "DARWIN"]:
        # 通信管道中断，不处理中断信息，放弃后续数据
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        # 被操作系统KILL
        signal.signal(signal.SIGTERM, abortSignalHandler)

    # 设置程序运行的目录
    if not os.path.isdir(work):
        click.secho("Work directory [" + os.path.abspath(work) + "] does not exist or invalid.", err=True, fg="red")
        sys.exit(255)
    else:
        os.environ["T_WORK"] = os.path.abspath(work)

    # 设置Robot的引导文件位置
    os.environ["TEST_ROOT"] = os.path.join(os.path.dirname(__file__), "robot")

    # 设置需要执行的文件任务或者任务目录
    # 1. 可以为一个目录，该目录下所有robot文件（包括子目录）都会被运行
    # 2. 可以为一个文件，该文件将会被运行
    # 3. 可以为多个文件或者多个目录，中间用逗号隔开
    os.environ["JOB_LIST"] = job

    # 初始化进程日志
    os.environ["COLOREDLOGS_LEVEL_STYLES"] = \
        "spam=22;debug=28;verbose=34;notice=220;warning=202;success=118,bold;" \
        "error=background=red,bold;critical=background=red"
    LOG_FORMAT = "%(asctime)s - %(name)15s-[%(process)8d] - %(levelname)9s - %(message)s"
    fFormat = logging.Formatter(LOG_FORMAT)
    consoleLogHandler = logging.StreamHandler()
    consoleLogHandler.setFormatter(fFormat)
    consoleLogHandler.setLevel(logging.INFO)
    logger = logging.getLogger("runFarm")
    coloredlogs.install(
        level=consoleLogHandler.level,
        fmt=LOG_FORMAT,
        logger=logger,
        isatty=True
    )

    # 正式开始运行Case
    runRegress = Regress(
        maxProcess=parallel,
        scriptTimeout=jobtimeout,
        workerTimeout=workertimeout,
        logger=logger,
        jobList=os.environ["JOB_LIST"]
    )
    runRegress.run()
    logger.info("Regress end. Please read report from [" +
                os.path.abspath(os.path.join(os.environ["T_WORK"], "report", "report.html")) + "]")
    sys.exit(0)


# 主程序
if __name__ == "__main__":
    cli()
